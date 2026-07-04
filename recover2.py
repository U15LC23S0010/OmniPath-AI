import os

os.makedirs('static/css', exist_ok=True)
os.makedirs('templates', exist_ok=True)

with open('app.py', 'w') as f:
    f.write('''from flask import Flask, render_template, request, jsonify, send_from_directory
import os, io, PyPDF2
from agents import analyze_resume, debate_resume

app = Flask(__name__)
app.secret_key = 'omnipath-ai-key'

@app.route('/')
def index(): return render_template('index.html')

@app.route('/onboarding')
def onboarding(): return render_template('onboarding.html')

@app.route('/resume-studio')
def resume_studio(): return render_template('resume_studio.html')

@app.route('/manifest.json')
def manifest(): return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def sw(): return send_from_directory('static', 'sw.js')

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    file = request.files.get('file')
    if file and file.filename.endswith('.pdf'):
        pdf = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ''.join(p.extract_text() for p in pdf.pages)
        return jsonify(analyze_resume(text, request.form.get('target_role', '')))
    return jsonify({'error': 'Invalid file'}), 400

@app.route('/api/debate-resume', methods=['POST'])
def debate():
    return jsonify(debate_resume(request.json.get('resume_text', ''), request.json.get('target_role', '')))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
''')

with open('agents.py', 'w') as f:
    f.write('''
def analyze_resume(text, role):
    return {'ats_score': 85, 'rewritten_summary': f'Optimized for {role}.', 'suggestions': ['Add metrics.']}

def debate_resume(text, role):
    return {'dialogue': [{'agent': 'Recruiter', 'color': 'violet', 'text': 'Needs keywords!'}, {'agent': 'Manager', 'color': 'cyan', 'text': 'Strong metrics!'}]}
''')

with open('templates/base.html', 'w') as f:
    f.write('''<!DOCTYPE html><html><head><title>OmniPath AI</title><link rel="stylesheet" href="/static/css/style.css"></head><body>{% block content %}{% endblock %}</body></html>''')

with open('templates/index.html', 'w') as f:
    f.write('''{% extends 'base.html' %}{% block content %}<h1>OmniPath AI</h1><a href="/onboarding">Start</a>{% endblock %}''')

with open('templates/onboarding.html', 'w') as f:
    f.write('''{% extends 'base.html' %}{% block content %}<h1>Onboarding</h1><a href="/resume-studio">Next</a>{% endblock %}''')

with open('templates/resume_studio.html', 'w') as f:
    f.write('''{% extends 'base.html' %}{% block content %}<h1>Resume Studio</h1>
<input type="text" id="targetRole" placeholder="Role">
<input type="file" id="resumeFile" accept=".pdf">
<button onclick="analyze()">Analyze PDF</button>
<button onclick="debate()">Agent Debate</button>
<pre id="results"></pre>
<script>
function analyze() {
    let fd = new FormData();
    fd.append('file', document.getElementById('resumeFile').files[0]);
    fd.append('target_role', document.getElementById('targetRole').value);
    fetch('/api/upload-resume', {method: 'POST', body: fd}).then(r=>r.json()).then(d=>document.getElementById('results').innerText=JSON.stringify(d));
}
function debate() {
    fetch('/api/debate-resume', {method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({resume_text: 'test', target_role: document.getElementById('targetRole').value})}).then(r=>r.json()).then(d=>document.getElementById('results').innerText=JSON.stringify(d));
}
</script>{% endblock %}''')

with open('static/css/style.css', 'w') as f:
    f.write('body { background: #06070a; color: #00ffcc; font-family: sans-serif; padding: 20px; } button { background: #ff007f; color: white; padding: 10px; border: none; cursor: pointer; }')

