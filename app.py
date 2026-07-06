from flask import Flask, render_template, request, jsonify, send_from_directory, session
from markupsafe import escape
import os, io, PyPDF2
from agents import SharedMemory, CareerOrchestrator

app = Flask(__name__)
# Security: Environment variable for Flask secret key
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'omnipath-ai-key-fallback')

orchestrator = CareerOrchestrator()

# Security: File size limit (5MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def get_shared_memory():
    # Security: Session validation
    if 'mcp_context' not in session or not isinstance(session['mcp_context'], dict):
        session['mcp_context'] = {}
    
    sm = SharedMemory(session['mcp_context'])
    if 'profile' in session:
        sm.profile = session['profile']
    return sm

def save_shared_memory(sm):
    session['mcp_context'] = sm.to_dict()
    session['profile'] = sm.profile
    session.modified = True

def sanitize_input(data):
    if isinstance(data, str):
        return escape(data.strip())
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(i) for i in data]
    return data

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 5MB.'}), 413

@app.errorhandler(Exception)
def handle_exception(e):
    # Security: Graceful error handling
    return jsonify({'error': 'An internal server error occurred. Please try again later.'}), 500

# --- VIEWS ---
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
def salary_intelligence():
    return render_template('salary_intelligence.html')

@app.route('/linkedin-optimizer')
def linkedin_optimizer():
    return render_template('linkedin_optimizer.html')

@app.route('/career-recovery')
def career_recovery():
    return render_template('career_recovery.html')

@app.route('/mcp-hub')
def mcp_hub():
    return render_template('mcp_hub.html')

# --- PWA ASSETS ---
@app.route('/manifest.json')
def manifest(): return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def sw(): return send_from_directory('static', 'sw.js')

# --- MCP ENDPOINTS ---
@app.route('/mcp/context', methods=['GET'])
def mcp_context():
    sm = get_shared_memory()
    return jsonify(sm.to_dict())

@app.route('/mcp/agents', methods=['GET'])
def mcp_agents():
    # Returns registered agents from AgentRegistry
    return jsonify([{ 'name': a.name, 'description': a.description, 'tasks': a.supported_tasks, 'status': a.status } for a in orchestrator.registry.list_agents()])

@app.route('/mcp/status', methods=['GET'])
def mcp_status():
    sm = get_shared_memory()
    return jsonify(orchestrator.get_status(sm))

@app.route('/mcp/tasks', methods=['GET'])
def mcp_tasks():
    sm = get_shared_memory()
    return jsonify({
        'running': orchestrator.running_tasks,
        'completed': orchestrator.completed_tasks,
        'history': sm.execution_history
    })

# --- APIS ---
@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    file = request.files.get('file')
    # Security: PDF MIME validation
    if not file or file.mimetype != 'application/pdf' or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file format. Please upload a valid PDF file.'}), 400
        
    try:
        pdf = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ''.join(p.extract_text() for p in pdf.pages)
        
        text_lower = text.lower()
        resume_indicators = ['experience', 'education', 'skills', 'employment', 'work history', 'professional summary', 'objective', 'certifications', 'projects']
        match_count = sum(1 for word in resume_indicators if word in text_lower)
        
        if match_count < 2:
            return jsonify({'error': 'The uploaded document does not appear to be a resume.'}), 400
            
        sm = get_shared_memory()
        result = orchestrator.execute_task(sm, 'analyze_resume', text=text, role=sanitize_input(request.form.get('target_role', '')))
        save_shared_memory(sm)
        return jsonify(result)
    except Exception:
        return jsonify({'error': 'Failed to parse PDF file.'}), 400

@app.route('/api/debate-resume', methods=['POST'])
def debate():
    file = request.files.get('file')
    text = ""
    if file and file.mimetype == 'application/pdf' and file.filename.endswith('.pdf'):
        try:
            pdf = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ''.join(p.extract_text() for p in pdf.pages)
        except Exception:
            pass
            
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'debate_resume', text=text, role=sanitize_input(request.form.get('target_role', '')))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/save-profile', methods=['POST'])
def save_profile():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    sm.profile = {
        'name': data.get('name', ''),
        'email': data.get('email', ''),
        'linkedin': data.get('linkedin', ''),
        'portfolio': data.get('portfolio', ''),
        'goals': f"{data.get('experience', '')} {data.get('role', '')} in {data.get('sector', '')}",
        'role': data.get('role', ''),
        'sector': data.get('sector', ''),
        'skills': data.get('skills', ''),
        'achievement': data.get('achievement', ''),
        'experience': data.get('experience', 'mid'),
        'education': data.get('education', 'bachelors'),
        'workMode': data.get('workMode', 'Hybrid'),
        'targetSalary': data.get('targetSalary', ''),
        'country': data.get('country', 'us'),
        'location': data.get('location', '')
    }
    save_shared_memory(sm)
    return jsonify({"status": "success", "message": "Profile saved."})

@app.route('/api/readiness', methods=['GET'])
def get_readiness():
    return jsonify({"overall": 85})

@app.route('/api/skill-gap', methods=['POST'])
def skill_gap_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'analyze_skill_gap', role=data.get('target_role', 'Professional'), skills=data.get('current_skills', []))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/roadmap', methods=['POST'])
def roadmap_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'generate_roadmap', role=data.get('target_role', 'Professional'), timeline=data.get('timeline', '6'))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/portfolio', methods=['POST'])
def portfolio_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'generate_portfolio', role=data.get('target_role', 'Professional'), difficulty=data.get('difficulty', 'intermediate'))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/linkedin-optimize', methods=['POST'])
def linkedin_optimize_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'optimize_linkedin', role=data.get('role', ''), url=data.get('url', ''), skills=data.get('skills', ''), achievement=data.get('achievement', ''))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/career-recovery', methods=['POST'])
def career_recovery_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'generate_recovery_plan', 
                                       role=data.get('role', ''), 
                                       skills=data.get('skills', ''), 
                                       ats_score=data.get('ats_score', ''), 
                                       portfolio_status=data.get('portfolio_status', ''), 
                                       interview_feedback=data.get('interview_feedback', ''))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/interview-question', methods=['POST'])
def interview_question_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'get_interview_question', task='get_interview_question', role=data.get('role', 'Professional'), type=data.get('type', 'behavioral'), question_num=data.get('question_num', 1), experience=data.get('experience', 'mid'))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/evaluate-answer', methods=['POST'])
def evaluate_answer_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'evaluate_answer', task='evaluate_answer', question=data.get('question', ''), answer=data.get('answer', ''))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/career-plan', methods=['POST'])
def career_plan_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'generate_career_plan', interests=data.get('interests', []))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/match-jobs', methods=['POST'])
def match_jobs_api():
    role = sanitize_input(request.form.get('role', 'Professional'))
    remote = sanitize_input(request.form.get('remote', 'any'))
    salary_min = sanitize_input(request.form.get('salary_min', '0'))
    
    resume_text = ""
    file = request.files.get('resume')
    if file and file.mimetype == 'application/pdf' and file.filename.endswith('.pdf'):
        try:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                resume_text += page.extract_text() + " "
        except Exception as e:
            pass
                
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'match_jobs', role=role, remote=remote, salary_min=salary_min, resume_text=resume_text)
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/salary', methods=['POST'])
def salary_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'get_salary_data', role=data.get('role', ''), country=data.get('country', 'us'), state=data.get('state', ''), experience=data.get('experience', 0))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/linkedin', methods=['POST'])
def linkedin_api():
    data = sanitize_input(request.json)
    sm = get_shared_memory()
    result = orchestrator.execute_task(sm, 'optimize_linkedin', 
                                       role=data.get('target_role', data.get('role', '')),
                                       skills=data.get('skills', ''),
                                       achievements=data.get('achievements', ''),
                                       url=data.get('linkedin_url', ''))
    save_shared_memory(sm)
    return jsonify(result)

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    return jsonify({"status": "success", "message": "OmniPath Agent responded."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)
