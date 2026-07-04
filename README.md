OmniPath AI — Your End-to-End Career Intelligence Platform
Track: Agents for Good
Subtitle: A multi-agent AI system that guides job seekers from confusion to their dream offer — resume, skills, interviews, salary, and recovery, all in one place.

The Problem I Wanted to Solve
Every year, millions of people apply for hundreds of jobs and hear nothing back. They don't know why. Was it the resume? The skills? The way they answered an interview question? Or are they just applying to the wrong places?

I've seen this happen to people around me. Smart, qualified people who just don't know how to "play the game." They spend months in a loop — apply, wait, get rejected, apply again. No feedback, no direction, no support.

I built OmniPath AI to break that loop.

It's not just a resume builder. It's not just a job board. It's a full-stack AI career team — 9 specialized AI agents working together, each knowing who you are and what you're targeting — so you can stop guessing and start progressing.

What OmniPath AI Does
OmniPath AI is a web application built on Flask with a multi-agent backend. You set up your profile once — your name, target role, skills, experience level, education, and location — and every agent on the platform instantly knows your context. You don't re-enter anything.

Here's every agent in the system:

1. Resume Optimizer & ATS Scorer
You paste your resume, and the agent analyzes it against your target role. It gives you an ATS (Applicant Tracking System) score, highlights missing keywords, and rewrites weak bullet points with actual metrics. It then generates a complete, recruiter-ready resume summary.

2. Skill Gap Analyzer
You tell it your target role and current skills. It maps the gap — what the market expects vs. what you have — and gives you a ranked list of what to learn next, in what order, and why.

3. Learning Roadmap Generator
Based on your role and timeline, it generates a week-by-week or month-by-month learning plan. Certifications, resources, projects — all mapped out so you know exactly what to do from today until offer day.

4. Project & Portfolio Engine
This agent recommends real, industry-grade projects for your target role. Not toy projects — actual things you'd be proud to show a hiring manager. It generates a complete GitHub README with tech stack, architecture, and instructions for each project idea.

5. Interview Coach
A mock interview simulator. You choose your role, experience level, and question type (behavioral or technical). The agent asks you a question, you type your answer, and it scores your response on clarity, structure, relevance, and depth. It also suggests how to improve your answer.

6. Job Matcher & Salary Intelligence
The Job Matcher gives you a personalized job list based on your profile — company type, work mode, salary range — all matched to your background. The Salary Intelligence agent tells you exactly what you should be earning based on your role, skills, and location, so you never undersell yourself in an offer negotiation.

7. LinkedIn Profile Optimizer
You give it your target role, current skills, and one key achievement. It generates an optimized LinkedIn headline, a professional summary, and a connection message you can send to recruiters. It even gives you a headline score.

8. Career Recovery Agent
This is the most unique agent in the system.

If you've applied to 100 jobs and haven't gotten an offer, this agent diagnoses why. It asks you to rate your ATS score, portfolio strength, and the kind of rejection feedback you usually get. It then identifies the root cause — whether it's your resume, your portfolio, your interview skills, or your application strategy — and builds a personalized 3-phase recovery plan with immediate, executable next steps.

No other career tool does this.

The MCP Hub — Showing the Infrastructure Behind the Agents
One of the things I'm most proud of is the MCP Hub — a live infrastructure dashboard that shows how the agents are connected to their underlying Model Context Protocol (MCP) servers.

Each agent is bound to a specific MCP:

Agent	MCP Server
Resume Agent	Browser MCP
Skill Gap Agent	Documentation MCP
Project & Portfolio Engine	Git MCP
Interview Coach	Browser MCP
Career Recovery Agent	Filesystem MCP
The Hub shows live metrics — MCP Calls Today, Connected Servers (4/4), Success Rate, and Average Response Time — along with real-time streaming console logs and animated line charts for each server's usage. This makes the agent orchestration visible and tangible, not just theoretical.

How It All Works Together (The Architecture)

User Profile (Onboarding)
        ↓
  localStorage Cache
        ↓
 Shared Prefill Engine (base.html)
   ↓         ↓         ↓
Agent 1   Agent 2   Agent 3...
   ↓         ↓         ↓
Flask API Routes (/api/resume, /api/skill-gap, etc.)
        ↓
  agents.py (AI Logic Engine)
        ↓
    JSON Response → UI Rendering
The key design decision was the global prefill engine. In base.html, I wrote a prefillFromProfile() function that reads the user's profile from localStorage and automatically fills in form fields on every agent page. This creates the "initialize once, work everywhere" experience that makes the platform feel like a real product, not a collection of disconnected tools.

The backend is a clean Python Flask app. All AI logic lives in agents.py — a ~1,100+ line engine that handles scoring, keyword analysis, plan generation, and natural language output. No external AI API calls that cost money or require keys — it runs completely self-contained so any judge can spin it up instantly.

Why "Agents for Good"?
Career inequality is real.

People with access to career coaches, alumni networks, and professional mentors get hired faster and negotiate better salaries. People without those resources — first-generation professionals, career changers, people from smaller cities — are left to figure it out alone.

OmniPath AI is a free, open, AI-powered career team for anyone who needs one.

A student in Jaipur preparing for their first tech job gets the same quality of guidance as someone in Bangalore with a professional coach. A mid-career professional trying to pivot from sales to product management gets a structured roadmap instead of YouTube rabbit holes.

The Career Recovery Agent is a direct response to this inequality. It's for the people who are doing everything "right" but still not getting results — and have no one to tell them what's actually wrong. It gives them an honest, structured diagnosis and a path forward.

That's agents for good. Not just useful — actively reducing the gap.

Technical Stack
Backend: Python / Flask
Frontend: HTML5, CSS3, Vanilla JavaScript
AI Logic: Custom rule-based + heuristic agents in agents.py
Data Flow: LocalStorage → Flask Sessions → JSON API responses
Charts: Chart.js (live real-time streaming)
Icons: Lucide Icons
Deployment: Can be run locally (python app.py) or deployed on any Python-compatible cloud
No paid API keys. No external dependencies that need setup. Clone and run.

Design Decisions I'm Proud Of
1. Profile-first architecture. Most AI tools make you fill in the same context every single time. I designed the system so you do it once and every agent inherits it. This is the right way to build a multi-agent product.

2. The Career Recovery Agent. This was the hardest agent to design, because it required building a diagnostic engine — not just a generator. It had to ask the right questions, identify root causes, and sequence the advice in a way that's actually actionable. I'm proud of how it turned out.

3. MCP Hub as an education tool. Most hackathon projects hide their infrastructure. I surfaced it. The MCP Hub is a visual, real-time demonstration of how multi-agent orchestration works — which I think is genuinely useful for anyone trying to understand agent-based systems.

4. No placeholder data. Every field, every card, every output is dynamic and based on the user's actual profile. This is a working product, not a mockup.

What I Would Build Next
Real LLM integration (Gemini API) so the resume rewrites and interview feedback are even more nuanced
A persistent database so users can save their progress across sessions
Email delivery of reports so users can take their recovery plan offline
A browser extension that auto-fills job applications with the user's optimized profile
A peer comparison feature so users can benchmark their profile against others in their role
