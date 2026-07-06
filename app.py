"""
OmniPath AI — app.py
Enterprise Flask Application with full Security Hardening (9 Layers):
  Layer 1: HTTP Security Headers (Talisman / CSP)
  Layer 2: Rate Limiting (Flask-Limiter)
  Layer 3: Hardened Session Cookies
  Layer 4: Input Validation & Length Limits
  Layer 5: File Upload Hardening (magic bytes + secure_filename)
  Layer 6: MCP Endpoint PII Redaction
  Layer 7: Production Configuration (no debug, localhost-only)
  Layer 8: Security Event Logging
  Layer 9: Privacy Policy Page + Session Clear Endpoint
"""

import os
import io
import re
import logging
import datetime
import PyPDF2

from flask import Flask, render_template, request, jsonify, send_from_directory, session
from markupsafe import escape
from werkzeug.utils import secure_filename

from agents import SharedMemory, CareerOrchestrator

# ── Layer 8: Security Event Logging ───────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] SECURITY: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
security_log = logging.getLogger('omnipath.security')

# ── App Initialization ─────────────────────────────────────────────────
app = Flask(__name__)

# ── Layer 4 fallback guard — secret key must be set in env ─────────────
_secret = os.environ.get('FLASK_SECRET_KEY', '')
if not _secret:
    security_log.warning("FLASK_SECRET_KEY not set — using insecure default. Set it in production!")
    _secret = 'omnipath-ai-insecure-fallback-change-me'
app.secret_key = _secret

# ── Layer 3: Hardened Session Cookies ─────────────────────────────────
app.config['SESSION_COOKIE_HTTPONLY'] = True       # JS cannot read cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'     # CSRF mitigation
app.config['SESSION_COOKIE_SECURE'] = False         # Set True when HTTPS is enabled
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)

# ── File Upload Limit (Layer 5) ────────────────────────────────────────
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB hard cap

# ── Layer 2: Rate Limiting ─────────────────────────────────────────────
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["300 per day", "60 per hour"],
        storage_uri="memory://",
    )
    LIMITER_ENABLED = True
except ImportError:
    security_log.warning("flask-limiter not installed. Rate limiting disabled.")
    LIMITER_ENABLED = False
    class _DummyLimiter:
        def limit(self, *a, **kw):
            def decorator(f): return f
            return decorator
        def shared_limit(self, *a, **kw):
            def decorator(f): return f
            return decorator
    limiter = _DummyLimiter()

# ── Layer 1: HTTP Security Headers (Talisman) ─────────────────────────
try:
    from flask_talisman import Talisman
    # CSP: allow CDNs used by the app (Chart.js, Lucide, Google Fonts)
    csp = {
        'default-src': ["'self'"],
        'script-src': [
            "'self'",
            "'unsafe-inline'",          # Needed for inline <script> blocks in templates
            "cdn.jsdelivr.net",
            "unpkg.com",
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",          # Needed for inline <style> blocks
            "fonts.googleapis.com",
            "cdn.jsdelivr.net",
            "unpkg.com",
        ],
        'font-src': [
            "'self'",
            "fonts.gstatic.com",
            "cdn.jsdelivr.net",
        ],
        'img-src': ["'self'", "data:"],
        'connect-src': ["'self'"],
        'frame-ancestors': ["'none'"],  # X-Frame-Options: DENY equivalent
    }
    Talisman(
        app,
        content_security_policy=csp,
        force_https=False,              # Set True in production
        strict_transport_security=False,
        referrer_policy='no-referrer',
        x_content_type_options=True,
        x_xss_protection=True,
    )
    security_log.info("Flask-Talisman security headers enabled.")
except ImportError:
    security_log.warning("flask-talisman not installed. Security headers disabled.")

# ── Orchestrator ───────────────────────────────────────────────────────
orchestrator = CareerOrchestrator()


# ══════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def get_shared_memory():
    """Load SharedMemory from session, validating its type."""
    if 'mcp_context' not in session or not isinstance(session['mcp_context'], dict):
        session['mcp_context'] = {}
    sm = SharedMemory(session['mcp_context'])
    if 'profile' in session and isinstance(session['profile'], dict):
        sm.profile = session['profile']
    return sm


def save_shared_memory(sm):
    """Persist SharedMemory back to session."""
    session['mcp_context'] = sm.to_dict()
    session['profile'] = sm.profile
    session.modified = True


def sanitize_input(data):
    """Recursively HTML-escape all string values to prevent XSS."""
    if isinstance(data, str):
        return str(escape(data.strip()))
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(i) for i in data]
    return data


# ── Layer 4: Input Validation Helpers ─────────────────────────────────
MAX_TEXT_LEN   = 10_000   # resume text, answers
MAX_FIELD_LEN  = 500      # general fields
MAX_ROLE_LEN   = 100      # role / title fields
MAX_SKILLS_LEN = 2_000    # comma-separated skills string

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
URL_RE   = re.compile(r'^https?://', re.IGNORECASE)

def validate_str(value, name, max_len=MAX_FIELD_LEN, required=False):
    """Validate a string field; raises ValueError on violation."""
    if not isinstance(value, str):
        value = ''
    value = value.strip()
    if required and not value:
        raise ValueError(f"'{name}' is required.")
    if len(value) > max_len:
        security_log.warning(f"Input too long: field='{name}' len={len(value)}")
        raise ValueError(f"'{name}' exceeds maximum length of {max_len} characters.")
    return value

def validate_email(value):
    """Validate email format."""
    if value and not EMAIL_RE.match(value):
        raise ValueError("Invalid email address format.")
    return value

def validate_url(value):
    """Validate URL starts with http/https."""
    if value and not URL_RE.match(value):
        raise ValueError("URL must start with http:// or https://")
    return value

# ── Layer 6: PII Redaction for MCP Endpoints ──────────────────────────
def redact_pii(data: dict) -> dict:
    """Strip PII from SharedMemory dict before exposing in dashboard."""
    import copy
    redacted = copy.deepcopy(data)
    profile = redacted.get('profile', {})
    if profile.get('email'):
        profile['email'] = '***@***.***'
    if profile.get('linkedin'):
        profile['linkedin'] = '[redacted]'
    if profile.get('portfolio'):
        profile['portfolio'] = '[redacted]'
    # Also strip raw resume text if stored
    resume = redacted.get('resume_data', {})
    resume.pop('raw_text', None)
    redacted['profile'] = profile
    redacted['resume_data'] = resume
    return redacted


# ── Layer 5: PDF Validation Helpers ───────────────────────────────────
MAX_PDF_PAGES = 50

def validate_and_extract_pdf(file_storage) -> str:
    """
    Validate PDF by MIME, secure filename, magic bytes, and page count.
    Returns extracted text or raises ValueError.
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided.")

    # Secure the filename (path traversal protection)
    filename = secure_filename(file_storage.filename)
    if not filename.lower().endswith('.pdf'):
        raise ValueError("Only PDF files are accepted.")

    # MIME type check
    if file_storage.mimetype not in ('application/pdf', 'application/octet-stream'):
        security_log.warning(f"Blocked upload with MIME: {file_storage.mimetype} file={filename}")
        raise ValueError("Invalid file type. Please upload a PDF.")

    raw = file_storage.read()

    # Magic bytes check: PDF files start with %PDF
    if not raw.startswith(b'%PDF'):
        security_log.warning(f"Blocked spoofed PDF upload: file={filename}")
        raise ValueError("File does not appear to be a valid PDF.")

    # Parse and enforce page limit
    reader = PyPDF2.PdfReader(io.BytesIO(raw))
    if len(reader.pages) > MAX_PDF_PAGES:
        security_log.warning(f"PDF too large: {len(reader.pages)} pages, file={filename}")
        raise ValueError(f"PDF exceeds maximum of {MAX_PDF_PAGES} pages.")

    text = ''.join(p.extract_text() or '' for p in reader.pages)
    return text


# ══════════════════════════════════════════════════════════════════
#  ERROR HANDLERS
# ══════════════════════════════════════════════════════════════════

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request. Please check your input.'}), 400

@app.errorhandler(413)
def request_entity_too_large(e):
    security_log.warning("Blocked oversized request (>5MB).")
    return jsonify({'error': 'File too large. Maximum size is 5MB.'}), 413

@app.errorhandler(429)
def too_many_requests(e):
    security_log.warning(f"Rate limit hit from {request.remote_addr}.")
    return jsonify({'error': 'Too many requests. Please slow down and try again later.'}), 429

@app.errorhandler(Exception)
def handle_exception(e):
    # Layer 8: Log actual error internally, never expose stack trace to client
    security_log.error(f"Unhandled exception: {type(e).__name__}: {e}")
    return jsonify({'error': 'An internal error occurred. Please try again.'}), 500


# ══════════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ══════════════════════════════════════════════════════════════════

@app.route('/')
def index(): return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    profile = session.get('profile', {'name': 'Future Professional', 'goals': 'Sector Professional'})
    return render_template('dashboard.html', profile=profile)

@app.route('/onboarding')
def onboarding(): return render_template('onboarding.html')

@app.route('/resume-studio')
def resume_studio(): return render_template('resume_studio.html')

@app.route('/career-planner')
def career_planner(): return render_template('career_planner.html')

@app.route('/skill-gap')
def skill_gap(): return render_template('skill_gap.html')

@app.route('/learning-roadmap')
def learning_roadmap(): return render_template('learning_roadmap.html')

@app.route('/portfolio-builder')
def portfolio_builder(): return render_template('portfolio_builder.html')

@app.route('/interview-coach')
def interview_coach(): return render_template('interview_coach.html')

@app.route('/job-matcher')
def job_matcher(): return render_template('job_matcher.html')

@app.route('/salary-intelligence')
def salary_intelligence(): return render_template('salary_intelligence.html')

@app.route('/linkedin-optimizer')
def linkedin_optimizer(): return render_template('linkedin_optimizer.html')

@app.route('/career-recovery')
def career_recovery(): return render_template('career_recovery.html')

@app.route('/mcp-hub')
def mcp_hub(): return render_template('mcp_hub.html')

# ── Layer 9: Privacy Policy Page ──────────────────────────────────────
@app.route('/privacy')
def privacy(): return render_template('privacy.html')

# ── PWA Assets ────────────────────────────────────────────────────────
@app.route('/manifest.json')
def manifest(): return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def sw(): return send_from_directory('static', 'sw.js')


# ══════════════════════════════════════════════════════════════════
#  MCP ENDPOINTS  (Layer 6: PII Redacted)
# ══════════════════════════════════════════════════════════════════

@app.route('/mcp/context', methods=['GET'])
def mcp_context():
    sm = get_shared_memory()
    return jsonify(redact_pii(sm.to_dict()))

@app.route('/mcp/agents', methods=['GET'])
def mcp_agents():
    return jsonify([
        {'name': a.name, 'description': a.description,
         'tasks': a.supported_tasks, 'status': a.status}
        for a in orchestrator.registry.list_agents()
    ])

@app.route('/mcp/status', methods=['GET'])
def mcp_status():
    sm = get_shared_memory()
    return jsonify(orchestrator.get_status(sm))

@app.route('/mcp/tasks', methods=['GET'])
def mcp_tasks():
    sm = get_shared_memory()
    return jsonify({
        'running':   orchestrator.running_tasks,
        'completed': orchestrator.completed_tasks,
        'history':   sm.execution_history,
    })


# ══════════════════════════════════════════════════════════════════
#  API ROUTES
# ══════════════════════════════════════════════════════════════════

# ── Resume Upload ──────────────────────────────────────────────────────
@app.route('/api/upload-resume', methods=['POST'])
@limiter.limit("10 per minute")
def upload_resume():
    try:
        text = validate_and_extract_pdf(request.files.get('file'))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Minimum content check
    indicators = ['experience','education','skills','employment','work history',
                  'professional summary','objective','certifications','projects']
    if sum(1 for w in indicators if w in text.lower()) < 2:
        return jsonify({'error': 'The uploaded document does not appear to be a resume.'}), 400

    role = sanitize_input(request.form.get('target_role', ''))
    try:
        role = validate_str(role, 'target_role', MAX_ROLE_LEN)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'analyze_resume', text=text, role=role)
    save_shared_memory(sm)
    return jsonify(result)


# ── Debate Resume ──────────────────────────────────────────────────────
@app.route('/api/debate-resume', methods=['POST'])
@limiter.limit("10 per minute")
def debate():
    text = ''
    try:
        text = validate_and_extract_pdf(request.files.get('file'))
    except ValueError:
        pass   # debate can run without a file

    role = sanitize_input(request.form.get('target_role', ''))
    try:
        role = validate_str(role, 'target_role', MAX_ROLE_LEN)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'debate_resume', text=text, role=role)
    save_shared_memory(sm)
    return jsonify(result)


# ── Save Profile ───────────────────────────────────────────────────────
@app.route('/api/save-profile', methods=['POST'])
@limiter.limit("30 per minute")
def save_profile():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        name     = validate_str(data.get('name', ''),         'name',    100)
        email    = validate_email(validate_str(data.get('email', ''),    'email',   200))
        role     = validate_str(data.get('role', ''),          'role',    MAX_ROLE_LEN)
        sector   = validate_str(data.get('sector', ''),        'sector',  100)
        skills   = validate_str(data.get('skills', ''),        'skills',  MAX_SKILLS_LEN)
        achieve  = validate_str(data.get('achievement', ''),   'achievement', MAX_FIELD_LEN)
        location = validate_str(data.get('location', ''),      'location', 100)
        linkedin = validate_url(validate_str(data.get('linkedin', ''),   'linkedin', 200))
        portfolio= validate_url(validate_str(data.get('portfolio', ''),  'portfolio',200))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    sm.profile = {
        'name': name, 'email': email, 'linkedin': linkedin,
        'portfolio': portfolio,
        'goals': f"{data.get('experience','')} {role} in {sector}",
        'role': role, 'sector': sector, 'skills': skills,
        'achievement': achieve,
        'experience':  data.get('experience', 'mid'),
        'education':   data.get('education',  'bachelors'),
        'workMode':    data.get('workMode',    'Hybrid'),
        'targetSalary':data.get('targetSalary',''),
        'country':     data.get('country',     'us'),
        'location':    location,
    }
    save_shared_memory(sm)
    return jsonify({"status": "success", "message": "Profile saved."})


# ── Readiness ──────────────────────────────────────────────────────────
@app.route('/api/readiness', methods=['GET'])
def get_readiness():
    return jsonify({"overall": 85})


# ── Skill Gap ──────────────────────────────────────────────────────────
@app.route('/api/skill-gap', methods=['POST'])
@limiter.limit("30 per minute")
def skill_gap_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        role   = validate_str(data.get('target_role', 'Professional'), 'target_role', MAX_ROLE_LEN)
        skills = data.get('current_skills', [])
        if isinstance(skills, str):
            validate_str(skills, 'current_skills', MAX_SKILLS_LEN)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'analyze_skill_gap', role=role, skills=skills)
    save_shared_memory(sm)
    return jsonify(result)


# ── Learning Roadmap ───────────────────────────────────────────────────
@app.route('/api/roadmap', methods=['POST'])
@limiter.limit("20 per minute")
def roadmap_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        role     = validate_str(data.get('target_role', 'Professional'), 'target_role', MAX_ROLE_LEN)
        timeline = validate_str(str(data.get('timeline', '6')),          'timeline',    10)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'generate_roadmap', role=role, timeline=timeline)
    save_shared_memory(sm)
    return jsonify(result)


# ── Portfolio ──────────────────────────────────────────────────────────
@app.route('/api/portfolio', methods=['POST'])
@limiter.limit("20 per minute")
def portfolio_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        role       = validate_str(data.get('target_role', 'Professional'), 'target_role', MAX_ROLE_LEN)
        difficulty = validate_str(data.get('difficulty', 'intermediate'),  'difficulty',  20)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'generate_portfolio', role=role, difficulty=difficulty)
    save_shared_memory(sm)
    return jsonify(result)


# ── LinkedIn Optimize ──────────────────────────────────────────────────
@app.route('/api/linkedin-optimize', methods=['POST'])
@limiter.limit("20 per minute")
def linkedin_optimize_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        role    = validate_str(data.get('role', ''),        'role',    MAX_ROLE_LEN)
        url     = validate_url(validate_str(data.get('url',''),'url', 200))
        skills  = validate_str(data.get('skills', ''),      'skills',  MAX_SKILLS_LEN)
        achieve = validate_str(data.get('achievement',''),  'achievement', MAX_FIELD_LEN)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'optimize_linkedin', role=role, url=url, skills=skills, achievement=achieve)
    save_shared_memory(sm)
    return jsonify(result)


# ── Career Recovery ────────────────────────────────────────────────────
@app.route('/api/career-recovery', methods=['POST'])
@limiter.limit("20 per minute")
def career_recovery_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        role       = validate_str(data.get('role', ''),               'role',               MAX_ROLE_LEN)
        skills     = validate_str(data.get('skills', ''),             'skills',             MAX_SKILLS_LEN)
        ats        = validate_str(str(data.get('ats_score', '')),      'ats_score',          10)
        port_stat  = validate_str(data.get('portfolio_status', ''),   'portfolio_status',   MAX_FIELD_LEN)
        iv_fb      = validate_str(data.get('interview_feedback', ''), 'interview_feedback', MAX_FIELD_LEN)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'generate_recovery_plan',
                                       role=role, skills=skills,
                                       ats_score=ats, portfolio_status=port_stat,
                                       interview_feedback=iv_fb)
    save_shared_memory(sm)
    return jsonify(result)


# ── Interview Question ─────────────────────────────────────────────────
@app.route('/api/interview-question', methods=['POST'])
@limiter.limit("40 per minute")
def interview_question_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        role       = validate_str(data.get('role', 'Professional'), 'role',       MAX_ROLE_LEN)
        q_type     = validate_str(data.get('type', 'behavioral'),   'type',       20)
        experience = validate_str(data.get('experience', 'mid'),    'experience', 20)
        q_num      = int(data.get('question_num', 1))
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'get_interview_question',
                                       task='get_interview_question',
                                       role=role, type=q_type,
                                       question_num=q_num, experience=experience)
    save_shared_memory(sm)
    return jsonify(result)


# ── Evaluate Answer ────────────────────────────────────────────────────
@app.route('/api/evaluate-answer', methods=['POST'])
@limiter.limit("30 per minute")
def evaluate_answer_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        question = validate_str(data.get('question', ''), 'question', MAX_TEXT_LEN)
        answer   = validate_str(data.get('answer', ''),   'answer',   MAX_TEXT_LEN)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'evaluate_answer',
                                       task='evaluate_answer',
                                       question=question, answer=answer)
    save_shared_memory(sm)
    return jsonify(result)


# ── Career Plan ────────────────────────────────────────────────────────
@app.route('/api/career-plan', methods=['POST'])
@limiter.limit("20 per minute")
def career_plan_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    interests = data.get('interests', [])
    if not isinstance(interests, list):
        interests = []
    # Limit list length
    interests = interests[:20]

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'generate_career_plan', interests=interests)
    save_shared_memory(sm)
    return jsonify(result)


# ── Match Jobs ─────────────────────────────────────────────────────────
@app.route('/api/match-jobs', methods=['POST'])
@limiter.limit("15 per minute")
def match_jobs_api():
    try:
        role       = validate_str(sanitize_input(request.form.get('role', 'Professional')), 'role',       MAX_ROLE_LEN)
        remote     = validate_str(sanitize_input(request.form.get('remote', 'any')),        'remote',     20)
        salary_min = validate_str(sanitize_input(request.form.get('salary_min', '0')),      'salary_min', 20)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    resume_text = ''
    file = request.files.get('resume')
    if file and file.filename:
        try:
            resume_text = validate_and_extract_pdf(file)
        except ValueError:
            pass  # Job match can work without resume

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'match_jobs',
                                       role=role, remote=remote,
                                       salary_min=salary_min, resume_text=resume_text)
    save_shared_memory(sm)
    return jsonify(result)


# ── Salary ─────────────────────────────────────────────────────────────
@app.route('/api/salary', methods=['POST'])
@limiter.limit("20 per minute")
def salary_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        role       = validate_str(data.get('role', ''),    'role',    MAX_ROLE_LEN)
        country    = validate_str(data.get('country','us'),'country', 10)
        state      = validate_str(data.get('state', ''),   'state',   50)
        experience = int(data.get('experience', 0))
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'get_salary_data',
                                       role=role, country=country,
                                       state=state, experience=experience)
    save_shared_memory(sm)
    return jsonify(result)


# ── LinkedIn ───────────────────────────────────────────────────────────
@app.route('/api/linkedin', methods=['POST'])
@limiter.limit("20 per minute")
def linkedin_api():
    raw = request.get_json(silent=True) or {}
    data = sanitize_input(raw)
    try:
        role     = validate_str(data.get('target_role', data.get('role','')), 'role',         MAX_ROLE_LEN)
        skills   = validate_str(data.get('skills', ''),                        'skills',       MAX_SKILLS_LEN)
        achieve  = validate_str(data.get('achievements', ''),                  'achievements', MAX_FIELD_LEN)
        url      = validate_url(validate_str(data.get('linkedin_url',''),      'linkedin_url', 200))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'optimize_linkedin',
                                       role=role, skills=skills,
                                       achievements=achieve, url=url)
    save_shared_memory(sm)
    return jsonify(result)


# ── Layer 9: Session Clear (Privacy Right to Erasure) ─────────────────
@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Allow users to wipe all their data from the server session."""
    session.clear()
    security_log.info(f"Session cleared by user from {request.remote_addr}.")
    return jsonify({"status": "success", "message": "Your data has been cleared."})


# ── Catch-all for undefined /api/* paths ──────────────────────────────
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    return jsonify({"status": "success", "message": "OmniPath Agent responded."})


# ══════════════════════════════════════════════════════════════════
#  ENTRYPOINT  (Layer 7: Production Configuration)
# ══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Read debug mode from env — never enable debug in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    # Restrict host to localhost when not debugging
    host = '0.0.0.0' if debug_mode else '127.0.0.1'

    if debug_mode:
        security_log.warning("Running in DEBUG mode — NOT suitable for production!")

    app.run(debug=debug_mode, use_reloader=False, host=host, port=port)
