from flask import Flask, render_template, request, jsonify, send_from_directory, session
import os, io, PyPDF2
from agents import analyze_resume, debate_resume

app = Flask(__name__)
app.secret_key = 'omnipath-ai-key'

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

# --- APIS ---
@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    file = request.files.get('file')
    if file and file.filename.endswith('.pdf'):
        pdf = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ''.join(p.extract_text() for p in pdf.pages)
        
        # Check if it's actually a resume by looking for common resume headers
        text_lower = text.lower()
        resume_indicators = ['experience', 'education', 'skills', 'employment', 'work history', 'professional summary', 'objective', 'certifications', 'projects']
        match_count = sum(1 for word in resume_indicators if word in text_lower)
        
        if match_count < 2:
            return jsonify({'error': 'The uploaded document does not appear to be a resume. Please upload a valid resume PDF.'}), 400
            
        return jsonify(analyze_resume(text, request.form.get('target_role', '')))
    return jsonify({'error': 'Invalid file format. Please upload a PDF.'}), 400

@app.route('/api/debate-resume', methods=['POST'])
def debate():
    file = request.files.get('file')
    text = ""
    if file and file.filename.endswith('.pdf'):
        pdf = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ''.join(p.extract_text() for p in pdf.pages)
    return jsonify(debate_resume(text, request.form.get('target_role', '')))

@app.route('/api/save-profile', methods=['POST'])
def save_profile():
    data = request.json
    session['profile'] = {
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
    return jsonify({"status": "success", "message": "Profile saved."})

@app.route('/api/readiness', methods=['GET'])
def get_readiness():
    return jsonify({"overall": 85})

@app.route('/api/skill-gap', methods=['POST'])
def skill_gap_api():
    data = request.json
    role = data.get('target_role', 'Professional')
    skills = data.get('current_skills', [])
    from agents import analyze_skill_gap
    return jsonify(analyze_skill_gap(role, skills))

@app.route('/api/roadmap', methods=['POST'])
def roadmap_api():
    data = request.json
    role = data.get('target_role', 'Professional')
    timeline = data.get('timeline', '6')
    from agents import generate_roadmap
    return jsonify(generate_roadmap(role, timeline))

@app.route('/api/portfolio', methods=['POST'])
def portfolio_api():
    data = request.json
    role = data.get('target_role', 'Professional')
    difficulty = data.get('difficulty', 'intermediate')
    from agents import generate_portfolio
    return jsonify(generate_portfolio(role, difficulty))

@app.route('/api/linkedin-optimize', methods=['POST'])
def linkedin_optimize_api():
    data = request.json
    role = data.get('role', '')
    url = data.get('url', '')
    skills = data.get('skills', '')
    achievement = data.get('achievement', '')
    from agents import optimize_linkedin
    return jsonify(optimize_linkedin(role, url, skills, achievement))

@app.route('/api/career-recovery', methods=['POST'])
def career_recovery_api():
    data = request.json
    role = data.get('role', '')
    skills = data.get('skills', '')
    ats_score = data.get('ats_score', '')
    portfolio_status = data.get('portfolio_status', '')
    interview_feedback = data.get('interview_feedback', '')
    from agents import generate_recovery_plan
    return jsonify(generate_recovery_plan(role, skills, ats_score, portfolio_status, interview_feedback))

@app.route('/api/interview-question', methods=['POST'])
def interview_question_api():
    data = request.json
    role = data.get('role', 'Professional')
    q_type = data.get('type', 'behavioral')
    q_num = data.get('question_num', 1)
    experience = data.get('experience', 'mid')
    from agents import get_interview_question
    return jsonify(get_interview_question(role, q_type, q_num, experience))

@app.route('/api/evaluate-answer', methods=['POST'])
def evaluate_answer_api():
    data = request.json
    question = data.get('question', '')
    answer = data.get('answer', '')
    from agents import evaluate_answer
    return jsonify(evaluate_answer(question, answer))

@app.route('/api/career-plan', methods=['POST'])
def career_plan_api():
    data = request.json
    from agents import generate_career_plan
    return jsonify(generate_career_plan(data.get('interests', [])))

@app.route('/api/match-jobs', methods=['POST'])
def match_jobs_api():
    role = request.form.get('role', 'Professional')
    remote = request.form.get('remote', 'any')
    salary_min = request.form.get('salary_min', '0')
    
    resume_text = ""
    if 'resume' in request.files:
        file = request.files['resume']
        if file and file.filename.endswith('.pdf'):
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    resume_text += page.extract_text() + " "
            except Exception as e:
                print("Error parsing PDF:", e)
                
    from agents import match_jobs
    return jsonify(match_jobs(role, remote, salary_min, resume_text))

@app.route('/api/salary', methods=['POST'])
def salary_api():
    data = request.json
    from agents import get_salary_data
    return jsonify(get_salary_data(data.get('role', ''), data.get('country', 'us'), data.get('state', ''), data.get('experience', 0)))

@app.route('/api/linkedin', methods=['POST'])
def linkedin_api():
    data = request.json
    from agents import optimize_linkedin
    return jsonify(optimize_linkedin(
        data.get('target_role', data.get('role', '')),
        data.get('skills', ''),
        data.get('achievements', ''),
        data.get('linkedin_url', '')
    ))

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    return jsonify({"status": "success", "message": "OmniPath Agent responded."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)

