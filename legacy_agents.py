"""
OmniPath AI - Agent Intelligence Engine
Multi-sector career AI logic for all 18 agents
"""
import random

# ────────────────────────────────────────────
# RESUME AGENT
# ────────────────────────────────────────────
def analyze_resume(text, role):
    text_lower = text.lower()
    
    role_keywords = {
        'software': ['python', 'java', 'react', 'sql', 'api', 'agile', 'aws', 'docker'],
        'data': ['python', 'sql', 'machine learning', 'tableau', 'statistics', 'pandas'],
        'manager': ['leadership', 'budget', 'strategy', 'cross-functional', 'kpi', 'stakeholder'],
        'default': ['communication', 'teamwork', 'leadership', 'results', 'project']
    }
    
    role_lower = role.lower() if role else ''
    if 'software' in role_lower or 'engineer' in role_lower or 'developer' in role_lower:
        keywords = role_keywords['software']
    elif 'data' in role_lower or 'analyst' in role_lower:
        keywords = role_keywords['data']
    elif 'manage' in role_lower or 'lead' in role_lower:
        keywords = role_keywords['manager']
    else:
        keywords = role_keywords['default']
        
    found = [k for k in keywords if k in text_lower]
    missing = [k for k in keywords if k not in text_lower]
    
    base_score = 50
    kw_score = (len(found) / max(len(keywords), 1)) * 25
    has_metrics = any(char.isdigit() for char in text)
    metric_score = 15 if has_metrics else 0
    has_contact = '@' in text_lower or 'linkedin.com' in text_lower
    contact_score = 5 if has_contact else 0
    
    score = min(98, round(base_score + kw_score + metric_score + contact_score))
    
    exp_level = "Experienced" if len(text.split()) > 400 else "Emerging"
    top_skills = ", ".join(found[:3]).title() if found else "key industry tools"
    summary = f"Results-driven and {exp_level.lower()} professional targeting {role or 'your next opportunity'}. Proven track record leveraging {top_skills} to deliver business value. Highly adaptable with a strong foundation in core industry methodologies."
    
    suggestions = []
    if missing:
        suggestions.append(f"Consider adding missing keywords to pass ATS: {', '.join(missing).title()}")
    if not has_metrics:
        suggestions.append("Your resume lacks quantifiable metrics. Add %, $, or numbers to describe achievements (e.g., 'Increased sales by 15%').")
    if not has_contact:
        suggestions.append("Make sure your email and LinkedIn URL are easily parsable by ATS systems.")
    if len(text.split()) > 800:
        suggestions.append("Your resume is quite long. Try to condense it to fit one or two pages for better readability.")
    elif len(text.split()) < 200:
        suggestions.append("Your resume is a bit sparse. Elaborate on your responsibilities and projects.")
        
    if len(suggestions) < 3:
        suggestions.append(f"Tailor your action verbs (e.g., 'Spearheaded', 'Optimized') to match the {role or 'target'} job description.")
        
    return {
        'ats_score': score,
        'rewritten_summary': summary,
        'suggestions': suggestions
    }

def debate_resume(text, role):
    text_lower = text.lower()
    word_count = len(text.split())
    has_metrics = any(char.isdigit() for char in text)
    has_education = 'education' in text_lower or 'university' in text_lower or 'bachelor' in text_lower

    recruiter_comment = (
        f"This resume is a good starting point for {role or 'the target role'}, but it's a bit long. Recruiters spend under 10 seconds scanning — cut it down." if word_count > 600 else
        f"The length is good, but without clear quantifiable metrics, it's hard to judge your impact for a {role or 'target'} position." if not has_metrics else
        f"Solid metrics and good length! Make sure your most impressive win is at the very top for {role or 'the target role'}."
    )
    
    ats_comment = (
        f"Keyword density analysis shows strong alignment with {role or 'target role'} descriptions. Good job avoiding complex formatting!" if len(text_lower) > 500 else
        f"Your resume is too brief. ATS scanners might reject this for lacking sufficient contextual keywords related to {role or 'the target role'}."
    )
    
    coach_comment = (
        "The structure looks solid. My recommendation: move your impact statement above education." if has_education else
        "I noticed you haven't clearly highlighted an education or certifications section. Even if self-taught, framing your learning path helps."
    )
    
    manager_comment = (
        f"For a {role or 'senior'} position, I need to see leadership impact within 3 seconds. Rewrite the summary to lead with your biggest career win." if not has_metrics else
        f"I like that you've included numbers. As a hiring manager for {role or 'this team'}, I want to see how you solved problems, not just what tools you used."
    )

    return {
        'dialogue': [
            {'agent': 'Recruiter Agent', 'color': 'violet', 'text': recruiter_comment},
            {'agent': 'ATS Scanner', 'color': 'cyan', 'text': ats_comment},
            {'agent': 'Career Coach', 'color': 'gold', 'text': coach_comment},
            {'agent': 'Hiring Manager', 'color': 'green', 'text': manager_comment}
        ]
    }

# ────────────────────────────────────────────
# SKILL GAP AGENT
# ────────────────────────────────────────────
def analyze_skill_gap(role, current_skills):
    current_lower = [s.lower() for s in current_skills]
    
    # Generate dynamic required skills based on role keywords
    role_lower = role.lower()
    required_skills = []
    
    if 'frontend' in role_lower or 'ui' in role_lower or 'web' in role_lower:
        required_skills.extend(['JavaScript', 'React/Vue/Angular', 'HTML/CSS', 'Responsive Design', 'Web Performance', 'Git'])
    elif 'backend' in role_lower or 'server' in role_lower:
        required_skills.extend(['Node.js/Python/Java', 'REST APIs', 'SQL/NoSQL', 'System Architecture', 'Docker/Containers', 'AWS/GCP/Azure'])
    elif 'software' in role_lower or 'engineer' in role_lower or 'developer' in role_lower:
        required_skills.extend(['Data Structures', 'Algorithms', 'System Design', 'Version Control (Git)', 'CI/CD', 'Testing/QA', 'Cloud Computing'])
    elif 'data' in role_lower or 'machine learning' in role_lower or 'ai' in role_lower:
        required_skills.extend(['Python', 'SQL', 'Machine Learning', 'Data Visualization', 'Statistics', 'Pandas/NumPy'])
    elif 'product' in role_lower or 'manager' in role_lower:
        required_skills.extend(['Product Strategy', 'Agile/Scrum', 'User Research', 'Data Analytics', 'Roadmapping', 'Stakeholder Management', 'A/B Testing'])
    elif 'design' in role_lower or 'ux' in role_lower or 'ui' in role_lower:
        required_skills.extend(['Figma/Sketch', 'User Research', 'Wireframing', 'Prototyping', 'Usability Testing', 'Design Systems'])
    elif 'market' in role_lower or 'seo' in role_lower:
        required_skills.extend(['SEO/SEM', 'Content Strategy', 'Google Analytics', 'Digital Marketing', 'CRM Tools', 'Copywriting'])
    elif 'finance' in role_lower or 'account' in role_lower:
        required_skills.extend(['Financial Modeling', 'Excel (Advanced)', 'Valuation', 'Risk Analysis', 'GAAP', 'Accounting Software'])
    else:
        # Fallback to a generic professional set + the role name itself as a specialized domain
        required_skills = [f'{role.title()} Core Principles', 'Project Management', 'Data Analysis', 'Cross-functional Communication', 'Strategic Planning', 'Domain Specific Tools', 'Leadership']
    
    # Remove duplicates but keep order
    required = list(dict.fromkeys(required_skills))
    
    gaps = []
    matched = []
    
    for req in required:
        req_lower = req.lower()
        req_parts = [p.strip() for p in req_lower.split('/')] if '/' in req_lower else [req_lower]
        
        is_matched = False
        for s in current_lower:
            for p in req_parts:
                # Split parenthetical parts, e.g. "Excel (Advanced)" -> "Excel"
                clean_p = p.split('(')[0].strip()
                if clean_p in s or s in clean_p:
                    is_matched = True
                    break
            if is_matched: break
                
        if is_matched:
            matched.append(req)
        else:
            gaps.append(req)

    score = round((len(matched) / len(required)) * 100) if required else 0
    critical = gaps[:3]
    important = gaps[3:]

    # Dynamic time and resources based on skill
    gap_details = []
    for g in gaps:
        priority = 'Critical' if g in critical else 'Important'
        time = '1-2 weeks' if 'Git' in g or 'HTML' in g else '4-8 weeks'
        resources = 'Coursera / Udemy' if 'Python' in g or 'SQL' in g else 'Industry Documentation / YouTube'
        gap_details.append({'name': g, 'priority': priority, 'time': time, 'resources': resources})

    return {
        'match_score': score,
        'summary': f"Based on industry standards for {role}, you match {score}% of the core requirements. Focus on closing {len(critical)} critical gaps to be highly competitive.",
        'critical_gaps': critical,
        'important_gaps': important,
        'gap_details': gap_details,
        'matched_skills': matched
    }

# ────────────────────────────────────────────
# LEARNING ROADMAP AGENT
# ────────────────────────────────────────────
def generate_roadmap(role, timeline):
    months = int(timeline)
    role_lower = role.lower()
    
    # Determine domain-specific skills and courses
    if 'frontend' in role_lower or 'web' in role_lower or 'ui' in role_lower:
        s1, s2, s3, s4 = 'HTML/CSS/JS', 'React & State Management', 'Frontend Architecture', 'Web Performance & Accessibility'
        c1, c2, c3, c4 = 'Modern JavaScript Bootcamp', 'Advanced React Patterns', 'Frontend System Design', 'Web Vitals Optimization'
        cert = 'Meta Front-End Developer'
    elif 'backend' in role_lower or 'server' in role_lower:
        s1, s2, s3, s4 = 'Server-Side Logic', 'Database Design (SQL/NoSQL)', 'API Architecture', 'Microservices & Docker'
        c1, c2, c3, c4 = 'Node.js/Python Backend Course', 'Database Management Deep Dive', 'Building Scalable APIs', 'Docker & Kubernetes Fundamentals'
        cert = 'AWS Certified Developer'
    elif 'data' in role_lower or 'machine learning' in role_lower or 'ai' in role_lower:
        s1, s2, s3, s4 = 'Python & Pandas', 'Statistics & SQL', 'Machine Learning Models', 'Deep Learning & MLOps'
        c1, c2, c3, c4 = 'Python for Data Science', 'Applied Statistics', 'Machine Learning by Andrew Ng', 'Deep Learning Specialization'
        cert = 'Google Data Analytics Certificate'
    elif 'product' in role_lower or 'manager' in role_lower:
        s1, s2, s3, s4 = 'Product Discovery', 'Agile & Scrum', 'Data-Driven Decisions', 'Product Strategy'
        c1, c2, c3, c4 = 'Product Management 101', 'Agile Masterclass', 'Analytics for PMs', 'Advanced Product Strategy'
        cert = 'Certified Scrum Product Owner (CSPO)'
    elif 'design' in role_lower or 'ux' in role_lower or 'ui' in role_lower:
        s1, s2, s3, s4 = 'UX Research', 'Wireframing & Prototyping', 'Design Systems', 'Interaction Design'
        c1, c2, c3, c4 = 'Google UX Design', 'Figma Masterclass', 'Building Design Systems', 'Advanced Interaction Design'
        cert = 'Google UX Design Certificate'
    elif 'marketing' in role_lower or 'seo' in role_lower:
        s1, s2, s3, s4 = 'Digital Marketing', 'SEO & Content', 'Performance Marketing', 'Marketing Analytics'
        c1, c2, c3, c4 = 'Digital Marketing Fundamentals', 'SEO Specialization', 'Google Ads Masterclass', 'Google Analytics Certification'
        cert = 'Google Digital Marketing Certificate'
    elif 'finance' in role_lower or 'account' in role_lower:
        s1, s2, s3, s4 = 'Financial Accounting', 'Financial Modeling', 'Corporate Finance', 'Valuation & Risk'
        c1, c2, c3, c4 = 'Accounting Fundamentals', 'Excel for Financial Modeling', 'Corporate Finance 101', 'Advanced Valuation'
        cert = 'CFA Level 1 Prep / FMVA'
    else:
        s1, s2, s3, s4 = f'{role} Fundamentals', 'Core Methodologies', 'Advanced Applications', 'Industry Leadership'
        c1, c2, c3, c4 = f'Intro to {role}', 'Practical Workshops', 'Advanced Problem Solving', 'Leadership in the Industry'
        cert = f'Certified {role} Professional'

    phases = []
    if months <= 3:
        phases = [
            {'phase': 1, 'title': 'Rapid Foundations', 'duration': 'Month 1', 'description': f'Core fundamentals required for {role}', 'topics': [{'skill': s1, 'course': c1, 'platform': 'Coursera', 'duration': '2 weeks', 'type': 'Course'}, {'skill': s2, 'course': c2, 'platform': 'Udemy', 'duration': '2 weeks', 'type': 'Course'}], 'milestone': 'Complete foundation assessment'},
            {'phase': 2, 'title': 'Applied Skills & Launch', 'duration': 'Month 2-3', 'description': 'Real-world application of core skills', 'topics': [{'skill': s3, 'course': c3, 'platform': 'LinkedIn Learning', 'duration': '4 weeks', 'type': 'Project'}, {'skill': s4, 'course': 'Capstone Project', 'platform': 'Self-directed', 'duration': '4 weeks', 'type': 'Portfolio'}], 'milestone': 'Build 2 portfolio projects'}
        ]
        certs = [cert, f'{role} Foundations Badge']
        commit = '25-30 hrs/week'
    elif months <= 6:
        phases = [
            {'phase': 1, 'title': 'Foundations', 'duration': 'Month 1-2', 'description': f'Building core knowledge for {role}', 'topics': [{'skill': s1, 'course': c1, 'platform': 'Coursera', 'duration': '4 weeks', 'type': 'Course'}, {'skill': s2, 'course': c2, 'platform': 'Udemy', 'duration': '4 weeks', 'type': 'Course'}], 'milestone': 'Pass foundations quiz'},
            {'phase': 2, 'title': 'Core Competency', 'duration': 'Month 3-4', 'description': 'Building professional-grade skills', 'topics': [{'skill': s3, 'course': c3, 'platform': 'LinkedIn Learning', 'duration': '5 weeks', 'type': 'Course'}, {'skill': f'{s1} & {s2} Applied', 'course': 'Deep Dive Workshop', 'platform': 'edX', 'duration': '3 weeks', 'type': 'Project'}], 'milestone': 'Complete 1 real project'},
            {'phase': 3, 'title': 'Advanced & Portfolio', 'duration': 'Month 5-6', 'description': 'Becoming job-ready with credentials', 'topics': [{'skill': s4, 'course': c4, 'platform': 'Pluralsight', 'duration': '4 weeks', 'type': 'Project'}, {'skill': 'Interview Prep', 'course': 'Mock Interviews', 'platform': 'OmniPath AI', 'duration': '4 weeks', 'type': 'Career'}], 'milestone': 'Obtain industry certification'}
        ]
        certs = [cert, f'Advanced {role} Certification']
        commit = '15-20 hrs/week'
    else:
        phases = [
            {'phase': 1, 'title': 'Deep Foundations', 'duration': 'Month 1-3', 'description': 'Comprehensive understanding of fundamentals', 'topics': [{'skill': s1, 'course': c1, 'platform': 'Coursera/edX', 'duration': '6 weeks', 'type': 'Course'}, {'skill': s2, 'course': c2, 'platform': 'Udemy', 'duration': '6 weeks', 'type': 'Course'}], 'milestone': 'Complete all foundation modules'},
            {'phase': 2, 'title': 'Specialization', 'duration': 'Month 4-7', 'description': 'Developing a specialized skill set', 'topics': [{'skill': s3, 'course': c3, 'platform': 'Coursera', 'duration': '8 weeks', 'type': 'Course'}, {'skill': 'Applied Projects', 'course': 'Real World Problems', 'platform': 'GitHub / Kaggle', 'duration': '8 weeks', 'type': 'Project'}], 'milestone': 'Publish 3 portfolio projects'},
            {'phase': 3, 'title': 'Advanced Mastery', 'duration': 'Month 8-10', 'description': 'Expert-level skills and leadership', 'topics': [{'skill': s4, 'course': c4, 'platform': 'Pluralsight', 'duration': '6 weeks', 'type': 'Course'}, {'skill': 'Industry Tools Deep Dive', 'course': 'Advanced Tooling', 'platform': 'Official Docs', 'duration': '6 weeks', 'type': 'Practice'}], 'milestone': 'Earn industry certification'},
            {'phase': 4, 'title': 'Job Ready', 'duration': 'Month 11-12', 'description': 'Final polish and job application', 'topics': [{'skill': 'Interview Prep', 'course': 'Mock Interviews', 'platform': 'OmniPath AI', 'duration': '4 weeks', 'type': 'Practice'}, {'skill': 'Resume & Portfolio', 'course': 'Career Optimization', 'platform': 'OmniPath AI', 'duration': '4 weeks', 'type': 'Career'}], 'milestone': 'Land first job interview'}
        ]
        certs = [f'Expert {role} Certification', cert, 'LinkedIn Learning Badge']
        commit = '10-15 hrs/week'

    return {
        'target_role': role,
        'timeline': f'{timeline}-Month',
        'weekly_commitment': commit,
        'phases': phases,
        'certifications': certs
    }

# ────────────────────────────────────────────
# PORTFOLIO BUILDER AGENT
# ────────────────────────────────────────────
def generate_portfolio(role, difficulty='intermediate'):
    role_lower = role.lower()
    domain = 'default'
    if 'data' in role_lower or 'analyst' in role_lower or 'scientist' in role_lower or 'ai' in role_lower: domain = 'data'
    elif 'frontend' in role_lower or 'ui dev' in role_lower or 'web' in role_lower: domain = 'frontend'
    elif 'backend' in role_lower or 'server' in role_lower: domain = 'backend'
    elif 'software' in role_lower or 'developer' in role_lower or 'engineer' in role_lower or 'programmer' in role_lower: domain = 'software'
    elif 'design' in role_lower or 'ux' in role_lower or 'ui' in role_lower or 'figma' in role_lower: domain = 'design'
    elif 'market' in role_lower or 'seo' in role_lower or 'content' in role_lower: domain = 'marketing'
    elif 'finance' in role_lower or 'account' in role_lower or 'invest' in role_lower: domain = 'finance'
    elif 'product' in role_lower or 'manager' in role_lower or 'agile' in role_lower: domain = 'product'

    if difficulty == 'beginner':
        time, comp = '1-2 weeks', 'Beginner'
        verbs = ['Build', 'Create', 'Design', 'Set up', 'Implement', 'Draft']
        adjs = ['Simple', 'Basic', 'Starter', 'Foundational', 'Core', 'Introductory']
    elif difficulty == 'advanced':
        time, comp = '4-8 weeks', 'Advanced'
        verbs = ['Architect', 'Engineer', 'Deploy', 'Scale', 'Optimize', 'Productionize']
        adjs = ['Enterprise', 'Scalable', 'High-Performance', 'Distributed', 'Advanced', 'Comprehensive']
    else:
        time, comp = '2-4 weeks', 'Intermediate'
        verbs = ['Develop', 'Integrate', 'Automate', 'Manage', 'Build', 'Streamline']
        adjs = ['Interactive', 'Dynamic', 'Automated', 'Full-stack', 'Integrated', 'Practical']

    domain_data = {
        'frontend': (
            ['E-commerce Storefront', 'Kanban Board', 'Social Media Feed', 'Analytics Dashboard', 'Booking System', 'Portfolio Template'],
            ['React/Vue', 'Tailwind CSS', 'State Management', 'REST APIs', 'Figma', 'Vercel']
        ),
        'backend': (
            ['RESTful API', 'Authentication Service', 'Job Queue System', 'Web Scraper', 'Chat Server', 'Payment Gateway Integration'],
            ['Node.js/Python', 'PostgreSQL', 'Redis', 'Docker', 'JWT', 'AWS/GCP']
        ),
        'software': (
            ['CLI Tool', 'Microservices Architecture', 'CRUD Application', 'Algorithm Visualizer', 'Test Automation Suite', 'File Sync System'],
            ['Java/C++/Go', 'System Design', 'Git/CI-CD', 'Unit Testing', 'Databases', 'Linux']
        ),
        'data': (
            ['Churn Predictor', 'Sales Dashboard', 'Recommendation Engine', 'NLP Classifier', 'Time-Series Forecaster', 'ETL Pipeline'],
            ['Python', 'Pandas', 'scikit-learn', 'SQL', 'Tableau/PowerBI', 'TensorFlow']
        ),
        'design': (
            ['FinTech Redesign', 'SaaS Design System', 'Onboarding Flow', 'E-commerce Checkout', 'Mobile App Wireframes', 'Accessibility Audit'],
            ['Figma', 'User Research', 'Prototyping', 'Wireframing', 'Design Tokens', 'Usability Testing']
        ),
        'marketing': (
            ['GTM Launch Strategy', 'Email Nurture Campaign', 'SEO Audit Report', 'Social Media Calendar', 'Paid Ad Campaign', 'Conversion Funnel'],
            ['Google Analytics', 'HubSpot', 'SEO Tools', 'Copywriting', 'A/B Testing', 'Excel']
        ),
        'finance': (
            ['DCF Valuation Model', 'Expense Tracker', 'Portfolio Risk Analysis', 'Financial Forecasting', 'Market Research Report', 'Budget Allocation Tool'],
            ['Excel/Google Sheets', 'Financial Modeling', 'Bloomberg', 'Data Analysis', 'Power Query', 'Risk Assessment']
        ),
        'product': (
            ['PRD & User Stories', 'Feature Roadmap', 'Analytics Audit', 'Competitor Analysis', 'Go-to-Market Plan', 'Sprint Backlog'],
            ['Jira/Confluence', 'Agile/Scrum', 'Mixpanel', 'Product Strategy', 'User Interviews', 'RICE Framework']
        ),
        'default': (
            ['Workflow Automation', 'Performance Dashboard', 'Strategy Framework', 'Resource Tracker', 'Client Portal', 'Data Analyzer'],
            ['Industry Tools', 'Data Analysis', 'Project Management', 'Communication', 'Strategy', 'Reporting']
        )
    }

    nouns, tech = domain_data[domain]
    
    projects = []
    for i in range(6):
        title = f"{adjs[i]} {nouns[i]}"
        desc = f"{verbs[i]} a {title.lower()} tailored for {role} use cases. Focuses on mastering {tech[i]} and {tech[(i+1)%6]}."
        
        readme = f"""# {title} 🚀

<div align="center">
  <p><strong>A professional-grade implementation tailored for {role} use cases.</strong></p>
  <p>Built with {tech[i]} and {tech[(i+1)%6]}</p>
</div>

---

## 📖 Overview
{desc}

This project serves as a comprehensive portfolio piece demonstrating advanced competency in modern development paradigms. It tackles real-world challenges faced by {role} professionals, prioritizing clean architecture, scalability, and maintainability.

## ✨ Key Features
- **Core Implementation**: Fully functional MVP focusing on {nouns[i].lower()}.
- **Advanced {tech[i]} Integration**: Utilizes best practices and advanced patterns.
- **Scalable Architecture**: Designed to handle increased loads and extended feature sets.
- **Robust Error Handling**: Comprehensive edge-case management and logging.

## 🛠️ Tech Stack & Architecture
- **Primary Framework**: `{tech[i]}`
- **Secondary Tooling**: `{tech[(i+1)%6]}`
- **Infrastructure / Support**: `{tech[(i+2)%6]}`
- **Design Pattern**: Module-driven architecture ensuring separation of concerns.

## 🚀 Getting Started

### Prerequisites
Before you begin, ensure you have the following installed:
- Relevant runtime environment for {tech[i]}
- Git

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/{role.replace(' ', '-').lower()}-proj-{i+1}.git
   cd {role.replace(' ', '-').lower()}-proj-{i+1}
   ```
2. **Install dependencies**
   ```bash
   # Use the package manager standard for {tech[i]}
   npm install  # or pip install, cargo build, etc.
   ```
3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Add your specific API keys and configuration
   ```

### Running the Application
```bash
npm run dev # or equivalent start command
```

## 📊 Results & Impact
- Successfully implemented core features for {nouns[i]} with a {comp} complexity level.
- Achieved target performance metrics (e.g., < 200ms response time, 99% uptime).
- Demonstrated senior-level proficiency in {tech[i]} and {tech[(i+1)%6]}.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! 
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
"""
        projects.append({
            'title': title,
            'description': desc,
            'tech_stack': [tech[i], tech[(i+1)%6], tech[(i+2)%6]],
            'estimated_time': time,
            'complexity': comp,
            'slug': f"{role.replace(' ', '-').lower()}-proj-{i+1}",
            'readme': readme
        })

    return {'projects': projects}

# ────────────────────────────────────────────
# INTERVIEW COACH AGENT
# ────────────────────────────────────────────
import random
import hashlib

def get_interview_question(role, q_type, q_num, experience='mid'):
    role_title = role.title() if role else 'Professional'
    role_lower = role.lower()
    
    # Create a stable seed so refreshing doesn't randomly swap the current question
    # but it feels infinitely dynamic across different roles/numbers
    seed_str = f"{role_lower}_{q_type}_{experience}_{q_num}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    random.seed(seed)
    
    # Tech domains
    if 'frontend' in role_lower or 'ui' in role_lower or 'web' in role_lower:
        techs = ['React state management', 'CSS Grid/Flexbox', 'Web Performance (LCP/CLS)', 'component reusability', 'cross-browser compatibility', 'DOM manipulation', 'frontend architecture']
    elif 'backend' in role_lower or 'server' in role_lower:
        techs = ['database indexing', 'REST API design', 'microservices architecture', 'rate-limiting', 'caching with Redis', 'handling race conditions', 'OAuth/JWT authentication']
    elif 'data' in role_lower or 'ml' in role_lower or 'ai' in role_lower:
        techs = ['data pipeline optimization', 'handling missing data', 'bias-variance tradeoff', 'model deployment', 'SQL query optimization', 'feature engineering', 'model drift monitoring']
    else:
        techs = ['system architecture', 'process optimization', 'cross-functional collaboration', 'technical debt', 'algorithm optimization', 'scalability', 'data security']

    # Dynamic generation
    if q_type == 'behavioral':
        situations = [
            "faced a critical deadline with insufficient resources",
            "had to convince a reluctant stakeholder",
            "discovered a major flaw in a project late in the game",
            "had to work with a difficult team member",
            "took the initiative to improve a broken process",
            "failed to meet a key objective",
            "had to learn a complex new technology over the weekend",
            "disagreed with your manager's technical approach"
        ]
        actions = [
            "How did you prioritize your actions?",
            "What was your step-by-step approach?",
            "How did you communicate this to the rest of the team?",
            "What compromises did you have to make?",
            "How did you ensure the final outcome was still successful?"
        ]
        
        if experience == 'junior':
            q = f"Tell me about a time you {random.choice(situations)} while learning your role as a {role_title}. {random.choice(actions)}"
        elif experience == 'senior':
            q = f"As a senior {role_title}, describe a situation where your team {random.choice(situations)}. {random.choice(actions)}"
        else:
            q = f"Describe a scenario in your {role_title} career where you {random.choice(situations)}. {random.choice(actions)}"
            
    elif q_type == 'technical':
        tasks = [
            "designing a highly scalable system from scratch",
            "troubleshooting a severe production outage",
            "migrating a legacy application to a modern stack",
            "evaluating a new technology for your team to adopt",
            "ensuring your deliverables are secure and compliant"
        ]
        tech = random.choice(techs)
        
        if experience == 'junior':
            q = f"Walk me through your fundamental understanding of {tech}. If you were stuck on an issue related to this, how would you debug it?"
        elif experience == 'senior':
            q = f"How would you approach {random.choice(tasks)} with a specific focus on {tech}? Discuss the trade-offs you would consider."
        else:
            q = f"Explain your approach to {random.choice(tasks)}. Specifically, how does {tech} play a role in your strategy?"
            
    elif q_type == 'hr':
        topics = [
            "handling high-pressure situations",
            "aligning your personal goals with the company's vision",
            "giving and receiving constructive feedback",
            "navigating sudden changes in company strategy",
            "motivating yourself and your peers"
        ]
        if experience == 'junior':
            q = f"Why are you passionate about starting your career as a {role_title}? Specifically, how do you approach {random.choice(topics)}?"
        elif experience == 'senior':
            q = f"With your extensive experience, what leadership philosophy do you bring to a {role_title} position? How do you handle {random.choice(topics)} across a team?"
        else:
            q = f"Where do you see your career as a {role_title} progressing over the next 3-5 years, especially when it comes to {random.choice(topics)}?"
            
    elif q_type == 'coding':
        verbs = ["Explain how you would handle", "Walk me through your approach to", "Describe the trade-offs of", "How would you optimize", "Explain the underlying concept of"]
        tech1 = random.choice(techs)
        tech2 = random.choice(techs)
        while tech1 == tech2:
            tech2 = random.choice(techs)
            
        q = f"{random.choice(verbs)} {tech1} in a complex {role_title} environment. How does this compare or interact with {tech2}?"

    tips = {
        'behavioral': 'Use the STAR method: Situation, Task, Action, Result. Be specific with outcomes.',
        'technical': 'Think aloud. Show your reasoning process, not just the final answer.',
        'hr': 'Be authentic and align your answer with the company culture. Research beforehand.',
        'coding': 'Clarify the problem, discuss your approach first, then write clean code.'
    }
    
    # Prepend encouraging phrase occasionally
    if q_num == 1:
        if experience == 'junior':
            q = f"Welcome! We love seeing fresh talent. {q}"
        elif experience == 'senior':
            q = f"It's great to speak with an experienced professional. {q}"
            
    return {
        'question': q,
        'number': q_num,
        'total': 8,
        'tips': tips.get(q_type, 'Take your time, be clear and concise.'),
        'type': q_type
    }

def evaluate_answer(question, answer):
    import re
    answer_lower = answer.lower()
    question_lower = question.lower()
    
    # Cheat Check: Did they just repeat the question back?
    clean_q = re.sub(r'[^\w\s]', '', question_lower)
    clean_a = re.sub(r'[^\w\s]', '', answer_lower)
    q_words = set(clean_q.split())
    a_words = set(clean_a.split())
    
    if len(q_words) > 0 and len(a_words) > 0:
        overlap = len(q_words.intersection(a_words))
        # If 70%+ of the question's words are in the answer, and the answer isn't much longer than the question
        if (overlap / len(q_words)) > 0.7 and len(a_words) < len(q_words) + 15:
            return {
                'score': 15,
                'strengths': ['You clearly read the question.'],
                'improvements': ['You appear to have just repeated the question back to me. Please provide a genuine, original answer to receive a proper evaluation.'],
                'model_answer_hint': f"Structure: Situation (20%) → Task (10%) → Action (50%) → Result (20%). Aim for 90-120 seconds verbally."
            }
            
    words = len(answer.split())
    
    has_metrics = any(char.isdigit() for char in answer)
    has_result = any(w in answer_lower for w in ['result', 'outcome', 'led to', 'achieved', 'increased', 'decreased', 'improved', 'delivered'])
    has_action = any(w in answer_lower for w in ['managed', 'developed', 'created', 'built', 'led', 'designed', 'implemented', 'optimized', 'spearheaded'])
    has_we = 'we ' in answer_lower or 'our team' in answer_lower
    has_i = ' i ' in answer_lower or answer_lower.startswith('i ')
    is_too_short = words < 30
    is_too_long = words > 200

    score = 50
    if not is_too_short: score += 15
    if has_metrics: score += 15
    if has_result: score += 10
    if has_action: score += 10
    
    strengths = []
    if has_metrics:
        strengths.append("Excellent use of quantifiable metrics to demonstrate impact.")
    if has_result:
        strengths.append("Strong focus on outcomes and results.")
    if has_action:
        strengths.append("Good use of strong action verbs to describe your contributions.")
    if words >= 50 and not is_too_long:
        strengths.append("Perfect answer length with a good level of detail.")
    if has_i and has_we:
        strengths.append("Great balance of highlighting personal contributions ('I') while acknowledging teamwork ('We').")
        
    if not strengths:
        strengths.append("Provided a clear, direct answer to the question.")
        strengths.append("Maintained a professional tone throughout the response.")
        
    improvements = []
    if is_too_short:
        improvements.append("Your answer is very brief. Try expanding using the STAR method (Situation, Task, Action, Result) to provide more context.")
    elif is_too_long:
        improvements.append("Your answer is a bit lengthy. Try to condense it to the most critical points to keep the interviewer engaged.")
        
    if not has_metrics:
        improvements.append("Try to include specific numbers, percentages, or timeframes to quantify your achievements.")
        
    if not has_result:
        improvements.append("Make sure to clearly state the final outcome or result of the situation you described.")
        
    if not has_i and has_we:
        improvements.append("You used 'We' a lot. Make sure to clearly specify what *your* specific role and actions were.")
        
    if not has_action:
        improvements.append("Use stronger action verbs (e.g., 'Spearheaded', 'Optimized', 'Engineered') to describe what you did.")

    if len(improvements) == 0:
        improvements.append("Your answer is very strong! Just remember to modulate your tone and pace when speaking verbally.")
        
    # Cap to top 3 for UI purposes
    strengths = strengths[:3]
    improvements = improvements[:3]

    return {
        'score': min(98, score),
        'strengths': strengths,
        'improvements': improvements,
        'model_answer_hint': f"Structure: Situation (20%) → Task (10%) → Action (50%) → Result (20%). Aim for 90-120 seconds verbally."
    }

# ────────────────────────────────────────────
# CAREER PLANNER AGENT
# ────────────────────────────────────────────
def generate_career_plan(interests=None):
    if not interests:
        interests = ['Technology', 'Business']
    
    interest_str = ", ".join(interests).title()
    
    recommendation = f"Based on your interests in {interest_str}, we've identified roles that balance your passions with strong market demand and growth potential."
    
    paths = [
        {
            'match': 95,
            'demand': 'High',
            'title': f'{interests[0].title()} Specialist' if len(interests) > 0 else 'Tech Consultant',
            'description': f'A role focusing on applying {interests[0] if len(interests) > 0 else "technology"} principles to solve complex industry problems.',
            'avg_salary': '$95,000',
            'timeline': '3-6 months',
            'skills_needed': [interests[0] if len(interests) > 0 else 'Analysis', 'Problem Solving', 'Project Management']
        },
        {
            'match': 88,
            'demand': 'Very High',
            'title': f'{interests[-1].title()} Analyst' if len(interests) > 0 else 'Business Analyst',
            'description': f'Analyzing trends and data within the {interests[-1] if len(interests) > 0 else "business"} domain to guide strategic decisions.',
            'avg_salary': '$85,000',
            'timeline': '2-4 months',
            'skills_needed': ['Data Analysis', interests[-1] if len(interests) > 0 else 'Strategy', 'Communication']
        },
        {
            'match': 82,
            'demand': 'Medium',
            'title': f'{interests[0].title()} Manager' if len(interests) > 0 else 'Product Manager',
            'description': f'Leading teams and projects centered around {interests[0] if len(interests) > 0 else "product development"}.',
            'avg_salary': '$110,000',
            'timeline': '1-2 years',
            'skills_needed': ['Leadership', 'Strategy', 'Cross-functional Teamwork']
        }
    ]
    
    next_steps = [
        f"Research top companies hiring for {paths[0]['title']} roles.",
        f"Identify 2-3 core skills needed for {paths[1]['title']} and find courses.",
        "Update your resume to highlight any past experience related to your interests.",
        "Connect with 5 professionals in these fields on LinkedIn."
    ]
    
    return {
        'recommendation': recommendation,
        'paths': paths,
        'next_steps': next_steps
    }

# ────────────────────────────────────────────
# JOB MATCHER AGENT
# ────────────────────────────────────────────
def match_jobs(role, remote_pref, salary_min_str, resume_text=""):
    import random
    
    # Extract keywords from resume text
    resume_lower = resume_text.lower()
    possible_skills = [
        'python', 'java', 'react', 'javascript', 'node', 'sql', 'aws', 'azure', 'docker', 
        'kubernetes', 'html', 'css', 'git', 'agile', 'scrum', 'machine learning', 
        'data analysis', 'figma', 'ui/ux', 'seo', 'marketing', 'leadership', 
        'strategy', 'operations', 'finance', 'excel', 'tableau'
    ]
    found_skills = [s for s in possible_skills if s in resume_lower]
    
    # Generate tailored skills based on role
    role_lower = role.lower()
    if 'frontend' in role_lower or 'ui' in role_lower:
        role_skills = ['React', 'Vue', 'CSS', 'JavaScript', 'TypeScript', 'Figma', 'Redux']
    elif 'backend' in role_lower or 'server' in role_lower:
        role_skills = ['Python', 'Java', 'Node.js', 'PostgreSQL', 'AWS', 'Docker', 'Kubernetes']
    elif 'data' in role_lower or 'ml' in role_lower or 'ai' in role_lower:
        role_skills = ['Python', 'SQL', 'TensorFlow', 'PyTorch', 'Pandas', 'Spark', 'Tableau']
    elif 'design' in role_lower or 'ux' in role_lower:
        role_skills = ['Figma', 'Adobe XD', 'Sketch', 'Prototyping', 'User Research', 'Wireframing']
    else:
        role_skills = ['Project Management', 'Agile', 'Leadership', 'Data Analysis', 'Strategy', 'Operations']
        
    platforms = ['LinkedIn', 'Naukri.com', 'Indeed', 'Glassdoor', 'Wellfound', 'Monster']
    companies = ['TechNova', 'Quantum Solutions', 'Apex Data Systems', 'Global Reach Media', 'Innovatech', 'DataSync Analytics', 'CloudNative Corp', 'NextGen Ventures', 'Google', 'Amazon', 'Microsoft']
    
    # Process salary minimum
    try:
        min_sal = int(''.join(filter(str.isdigit, str(salary_min_str))))
    except:
        min_sal = 60000
        
    if min_sal < 30000: min_sal = 60000
    
    generated_jobs = []
    
    for i in range(5):
        # Salary logic
        sal_base = min_sal + random.randint(0, 30000)
        sal_top = sal_base + random.randint(15000, 40000)
        
        # Location logic
        if remote_pref == 'remote':
            loc = 'Anywhere'
            rem = 'Fully Remote'
        elif remote_pref == 'hybrid':
            loc = random.choice(['New York, NY', 'San Francisco, CA', 'Austin, TX', 'London, UK', 'Toronto, ON', 'Bengaluru, IN'])
            rem = 'Hybrid'
        elif remote_pref == 'onsite':
            loc = random.choice(['New York, NY', 'San Francisco, CA', 'Austin, TX', 'London, UK', 'Toronto, ON', 'Bengaluru, IN'])
            rem = 'On-Site'
        else: # any
            rem = random.choice(['Fully Remote', 'Hybrid', 'On-Site'])
            loc = 'Anywhere' if rem == 'Fully Remote' else random.choice(['New York, NY', 'San Francisco, CA', 'Austin, TX', 'London, UK', 'Toronto, ON', 'Bengaluru, IN'])
            
        # Tags logic (mix of role skills)
        job_tags = random.sample(role_skills, min(3, len(role_skills)))
        
        # Score calculation based on overlap between resume skills and job tags
        overlap_count = sum(1 for tag in job_tags if tag.lower() in resume_lower)
        
        if overlap_count > 0:
            score = random.randint(90, 98)
        else:
            score = random.randint(75, 89)
            
        # If no resume was uploaded, give a generic high score
        if not resume_text:
            score = random.randint(80, 95)
            
        generated_jobs.append({
            'title': f"{random.choice(['Senior ', 'Lead ', '', 'Staff '])}{role.title() if role else 'Professional'}",
            'company': random.choice(companies),
            'platform': random.choice(platforms),
            'location': loc,
            'remote': rem,
            'salary': f"${sal_base:,} - ${sal_top:,}",
            'match': score,
            'description': f"Looking for an experienced {role.title() if role else 'candidate'} to join our dynamic team and drive key initiatives using {job_tags[0]} and {job_tags[1]}.",
            'tags': job_tags,
            'posted': random.randint(1, 14)
        })
        
    # Sort by match score descending
    generated_jobs.sort(key=lambda x: x['match'], reverse=True)
    
    summary = f"Found {len(generated_jobs)} highly relevant jobs for '{role.title()}' based on your resume profile and criteria."
    if not resume_lower.strip():
        summary = f"Found {len(generated_jobs)} jobs for '{role.title()}'. (Upload a resume for higher accuracy matching!)"
        
    return {
        'jobs': generated_jobs,
        'summary': summary
    }

# ────────────────────────────────────────────
# SALARY INTELLIGENCE AGENT
# ────────────────────────────────────────────
COUNTRY_DATA = {
    'india': {'currency': '₹', 'multiplier': 83.0, 'cost_index': 0.3},
    'in': {'currency': '₹', 'multiplier': 83.0, 'cost_index': 0.3},
    'uk': {'currency': '£', 'multiplier': 0.79, 'cost_index': 0.8},
    'united kingdom': {'currency': '£', 'multiplier': 0.79, 'cost_index': 0.8},
    'germany': {'currency': '€', 'multiplier': 0.92, 'cost_index': 0.85},
    'france': {'currency': '€', 'multiplier': 0.92, 'cost_index': 0.85},
    'canada': {'currency': 'C$', 'multiplier': 1.36, 'cost_index': 0.9},
    'australia': {'currency': 'A$', 'multiplier': 1.53, 'cost_index': 1.0},
    'singapore': {'currency': 'S$', 'multiplier': 1.34, 'cost_index': 1.1},
    'japan': {'currency': '¥', 'multiplier': 150.0, 'cost_index': 0.85},
    'us': {'currency': '$', 'multiplier': 1.0, 'cost_index': 1.0},
    'usa': {'currency': '$', 'multiplier': 1.0, 'cost_index': 1.0},
    'united states': {'currency': '$', 'multiplier': 1.0, 'cost_index': 1.0},
}

def get_salary_data(role, country_code, state_input, experience_years):
    import re
    
    # Base USD calculations (assuming 1.0 cost_index)
    base_usd = 60000
    
    role_lower = role.lower()
    if 'senior' in role_lower or 'lead' in role_lower: base_usd += 40000
    if 'manager' in role_lower or 'director' in role_lower: base_usd += 60000
    if 'data' in role_lower or 'machine learning' in role_lower: base_usd += 20000
    if 'software' in role_lower or 'engineer' in role_lower or 'developer' in role_lower: base_usd += 15000
    
    try:
        exp = float(experience_years)
    except:
        exp = 0.0
        
    # Add roughly $8,000 per year of experience
    base_usd += (exp * 8000)
    
    country_info = COUNTRY_DATA.get(country_code.lower(), COUNTRY_DATA['us'])
    
    # Apply cost of living and currency conversion
    adjusted_base = base_usd * country_info['cost_index'] * country_info['multiplier']
    
    median = round(adjusted_base / 1000) * 1000
    p25 = round((adjusted_base * 0.8) / 1000) * 1000
    p75 = round((adjusted_base * 1.25) / 1000) * 1000
    
    currency = country_info['currency']
    
    # Generate Locations Compare dynamically
    compare_cities = []
    
    c = country_code.lower()
    
    if c == 'india':
        cities = ['Bengaluru', 'Mumbai', 'Hyderabad']
        if state_input.lower() in ['maharashtra', 'mh']:
            cities = ['Mumbai', 'Pune', 'Nagpur']
        elif state_input.lower() in ['karnataka', 'ka']:
            cities = ['Bengaluru', 'Mysuru', 'Mangaluru']
    elif c in ['uk', 'united kingdom']:
        cities = ['London', 'Manchester', 'Edinburgh']
    elif c == 'japan':
        cities = ['Tokyo', 'Osaka', 'Kyoto']
    elif c == 'canada':
        cities = ['Toronto, ON', 'Vancouver, BC', 'Montreal, QC']
    elif c == 'australia':
        cities = ['Sydney, NSW', 'Melbourne, VIC', 'Brisbane, QLD']
    elif c == 'germany':
        cities = ['Berlin', 'Munich', 'Frankfurt']
    elif c == 'france':
        cities = ['Paris', 'Lyon', 'Marseille']
    elif c == 'singapore':
        cities = ['Central Area', 'Jurong', 'Woodlands']
    else:
        cities = ['San Francisco, CA', 'New York, NY', 'Austin, TX']
        if state_input.lower() in ['california', 'ca']:
            cities = ['San Francisco, CA', 'Los Angeles, CA', 'San Diego, CA']
        elif state_input.lower() in ['new york', 'ny']:
            cities = ['New York City', 'Buffalo', 'Rochester']
        elif state_input.lower() in ['texas', 'tx']:
            cities = ['Austin, TX', 'Dallas, TX', 'Houston, TX']
            
    for i, city in enumerate(cities):
        modifier = 1.2 if i == 0 else (1.1 if i == 1 else 0.95)
        compare_cities.append({
            'city': city,
            'median': round((median * modifier) / 1000) * 1000
        })

    # Scripts
    exp_str = f"{int(exp)} years" if exp > 0 else "my background"
    
    loc_display = f"{state_input.title()}, {country_code.upper()}" if state_input else f"{country_code.title()}"
    neg_script = f"Based on {exp_str} delivering results, and the current market rate for {role.title()}s in {loc_display}, I am looking for a base salary closer to {currency}{p75:,}. Is there flexibility to reach this number?"
    
    # Dynamic Negotiation Tips
    neg_tips = [
        f"Anchor high near your target of {currency}{p75:,} to leave room for negotiation.",
    ]
    
    # Experience-based tips
    if exp < 3:
        neg_tips.append("As an emerging professional, negotiate for learning stipends, certifications, and rapid review cycles if the base salary is inflexible.")
    elif exp > 7:
        neg_tips.append("At your senior level, heavily negotiate sign-on bonuses, equity/stock options (RSUs), and performance-based multipliers.")
    else:
        neg_tips.append("Leverage your proven track record to negotiate a higher base or an accelerated performance review at the 6-month mark.")
        
    # Country-based tips
    c = country_code.lower()
    if c in ['uk', 'united kingdom', 'germany', 'france']:
        neg_tips.append("In European markets, consider negotiating additional annual leave days, pension contributions, or a 4-day work week arrangement.")
    elif c in ['india', 'in']:
        neg_tips.append("In the Indian market, ensure you clearly understand the fixed vs. variable pay breakdown. Negotiate for higher fixed allowances (HRA, LTA).")
    elif c == 'japan':
        neg_tips.append("In Japan, emphasize long-term commitment and ask about commuting allowances, housing subsidies, and bi-annual bonus structures.")
    else:
        neg_tips.append("If base pay is capped, pivot to negotiating fully covered health premiums, remote work days, and 401k/retirement matching.")
        
    # Role-based tips
    if 'software' in role_lower or 'data' in role_lower or 'engineer' in role_lower:
        neg_tips.append("Tech roles often have flexibility for remote-work setups and home-office/hardware budgets. Request this if the salary falls short.")
    elif 'manager' in role_lower or 'director' in role_lower:
        neg_tips.append("Leadership roles should secure severance protections and clarify the exact metrics tied to your performance bonuses.")
        
    return {
        'median': median,
        'p25': p25,
        'p75': p75,
        'currency': currency,
        'demand': 'Very High' if 'data' in role_lower or 'software' in role_lower else 'Stable',
        'growth_forecast': '+12%' if exp < 5 else '+8%',
        'locations_compare': compare_cities,
        'negotiation_script': neg_script,
        'negotiation_tips': neg_tips
    }

# ────────────────────────────────────────────
# LINKEDIN OPTIMIZER AGENT
# ────────────────────────────────────────────
def optimize_linkedin(role, skills='', achievements='', linkedin_url=''):
    skills_list = [s.strip() for s in skills.split(',') if s.strip()] if skills else ['Strategic Thinking', 'Problem Solving', 'Leadership']
    skill1 = skills_list[0] if len(skills_list) > 0 else 'Strategic Thinking'
    skill2 = skills_list[1] if len(skills_list) > 1 else 'Problem Solving'
    skill3 = skills_list[2] if len(skills_list) > 2 else 'Cross-Functional Leadership'
    
    achievement_text = achievements if achievements else 'driving measurable results and leading high-impact initiatives'
    short_achieve = achievement_text[:40] + "..." if len(achievement_text) > 40 else achievement_text
    
    role_lower = role.lower()
    
    # 8-Domain Classification
    if any(k in role_lower for k in ['software', 'developer', 'engineer', 'programmer', 'full stack']):
        domain = 'engineering'
    elif any(k in role_lower for k in ['data', 'machine learning', 'ai', 'analytics', 'scientist']):
        domain = 'data'
    elif any(k in role_lower for k in ['design', 'ux', 'ui', 'creative', 'art', 'animator']):
        domain = 'design'
    elif any(k in role_lower for k in ['product', 'scrum', 'agile', 'owner']):
        domain = 'product'
    elif any(k in role_lower for k in ['market', 'seo', 'growth', 'content', 'brand']):
        domain = 'marketing'
    elif any(k in role_lower for k in ['sales', 'account', 'bdr', 'sdr', 'business development', 'revenue']):
        domain = 'sales'
    elif any(k in role_lower for k in ['finance', 'accountant', 'audit', 'tax', 'investment']):
        domain = 'finance'
    elif any(k in role_lower for k in ['hr', 'human resources', 'talent', 'recruiter', 'people']):
        domain = 'hr'
    else:
        domain = 'general'

    # Extract Name from URL
    extracted_name = "[Your Name]"
    tips = []
    
    if linkedin_url:
        import re
        url_clean = linkedin_url.lower().strip('/')
        if 'linkedin.com/in/' in url_clean:
            slug = url_clean.split('linkedin.com/in/')[-1].split('/')[0]
            clean_slug = re.sub(r'[\d\-]+$', '', slug)
            name_parts = [p.capitalize() for p in clean_slug.split('-') if p.isalpha()]
            if name_parts:
                extracted_name = " ".join(name_parts)
                tips.append(f"✅ Profile Extracted: Welcome, {extracted_name}!")
            
            if any(char.isdigit() for char in slug) and len(slug) > 10:
                tips.append("⚠️ URL Analysis: Your URL contains random numbers. Go to 'Edit public profile & URL' to create a clean, custom URL (e.g., /in/firstnamelastname).")
            else:
                tips.append("✅ URL Analysis: Your custom LinkedIn URL looks clean and professional!")
        else:
            tips.append("⚠️ Your LinkedIn URL format seems incorrect. Make sure it starts with 'linkedin.com/in/'.")
    else:
        tips.append("💡 Tip: Provide your LinkedIn URL next time so we can check if it's properly customized and extract your profile.")

    # Domain-Specific Templates
    if domain == 'engineering':
        headline = f"{role} | Architecting Scalable Systems | {skill1} & {skill2} | {short_achieve}"
        about = f"""Software engineering professional specializing in {role} with a deep passion for building robust architecture, clean code, and resilient infrastructure.
        
⚙️ Tech Stack & Expertise: {skill1}, {skill2}, {skill3}
🚀 Major Milestone: {achievement_text}

I thrive in fast-paced environments where I can tackle complex technical debt, optimize performance bottlenecks, and ship high-quality products to production. When I'm not coding, I'm exploring new frameworks or contributing to open-source tools.

Always open to discussing system design and connecting with fellow engineers!"""
        connection_message = f"Hi [Name],\n\nI was reviewing your engineering team's recent updates at [Company]. As a {role} currently working heavily with {skill1}, I'm always looking to connect with builders who are pushing technical boundaries.\n\nBest,\n{extracted_name}"
        recruiter_message = f"Hi [Recruiter's Name],\n\nI noticed you're sourcing technical talent for [Company]. I'm a {role} actively exploring new engineering challenges. Given my background in {skill1} (most recently {short_achieve}), I'd love to chat if there's a mutual fit on your current roadmap.\n\nThanks,\n{extracted_name}"
        tips.extend(["Attach your GitHub profile link directly in the 'Contact Info' section.", "Pin 2-3 of your best code repositories in the LinkedIn 'Featured' section."])

    elif domain == 'data':
        headline = f"{role} | Transforming Raw Data into Strategic Insights | {skill1} | {short_achieve}"
        about = f"""Data professional obsessed with finding the signal in the noise. As a {role}, I bridge the gap between complex datasets and actionable business strategy.

📊 Core Competencies: {skill1}, {skill2}, {skill3}
🎯 Impact: {achievement_text}

Whether it's deploying predictive models, optimizing data pipelines, or designing executive dashboards, I believe data is only as good as the story it tells. 

Let's connect if you love geeking out over algorithms, statistical analysis, or MLOps."""
        connection_message = f"Hi [Name],\n\nI came across your profile while researching [Company]'s data initiatives. As a {role} leveraging {skill1} to drive insights, I love connecting with other data-driven professionals.\n\nBest,\n{extracted_name}"
        recruiter_message = f"Hi [Recruiter's Name],\n\nI saw you're hiring for data roles at [Company]. I'm a {role} with deep expertise in {skill1} and {skill2}. Recently, I achieved {short_achieve}, and I'm currently looking for teams building advanced analytics solutions.\n\nWould love to connect,\n{extracted_name}"
        tips.extend(["Link your Kaggle profile or technical blog in your Featured section.", "Highlight specific metrics (e.g., 'improved model accuracy by 15%') in your Experience timeline."])

    elif domain == 'design':
        headline = f"{role} | Human-Centered Design | {skill1} | {short_achieve}"
        about = f"""I am a {role} obsessed with the intersection of human psychology and beautiful interfaces. 

✨ My toolkit includes: {skill1}, {skill2}, and {skill3}.
🏆 Proudest Milestone: {achievement_text}

I believe great design is completely invisible. I work closely with product and engineering to translate extremely complex requirements into seamless, accessible, and delightful user journeys. 

Let's talk about design systems, typography, and user empathy."""
        connection_message = f"Hi [Name],\n\nI absolutely loved [Company]'s recent product redesign. As a {role} focused on {skill1}, I'm deeply passionate about intuitive UX and wanted to add you to my network.\n\nBest,\n{extracted_name}"
        recruiter_message = f"Hi [Recruiter's Name],\n\nI noticed you hire creative talent for [Company]. I'm a {role} passionate about accessible design and {skill1}. After recently {short_achieve}, I'm looking for a new design-forward team to join.\n\nPortfolio is linked on my profile. Let's chat!\n\nBest,\n{extracted_name}"
        tips.extend(["Make sure your Behance, Dribbble, or personal portfolio link is the very first thing in your Featured section.", "Upload high-quality thumbnails of your design work directly to your Experience timeline."])

    elif domain == 'product':
        headline = f"{role} | Bridging Vision & Execution | {skill1} | {short_achieve}"
        about = f"""Strategic {role} with a track record of taking complex visions from zero-to-one and scaling them to market.

🧠 Key Strengths: {skill1}, {skill2}, {skill3}
📈 Massive Win: {achievement_text}

I am a ruthless prioritizer who deeply understands the balance between user needs, engineering constraints, and business ROI. I thrive in cross-functional chaos and love building products that people actually want to use.

Let's connect and talk product led growth!"""
        connection_message = f"Hi [Name],\n\nI've been following [Company]'s product trajectory and am super impressed. I'm a {role} specializing in {skill1}, and I'm always looking to connect with top-tier product minds.\n\nBest,\n{extracted_name}"
        recruiter_message = f"Hi [Recruiter's Name],\n\nI see you're sourcing Product leaders for [Company]. I'm a {role} with a strong track record in {skill1}. Most recently, I drove success by {short_achieve}. If you have openings that require cross-functional leadership, I'd love to connect.\n\nBest,\n{extracted_name}"
        tips.extend(["Pin a case study or a high-level product roadmap you developed in the Featured section.", "Ensure your experience emphasizes cross-functional leadership and stakeholder management."])

    elif domain == 'marketing':
        headline = f"{role} | Driving Growth & ROI via {skill1} | {short_achieve}"
        about = f"""Creative strategist and {role} who believes that the best marketing is both highly analytical and deeply human.

💡 Focus Areas: {skill1}, {skill2}, {skill3}
🚀 Major Campaign: {achievement_text}

I build brand narratives that convert. Whether it's scaling acquisition channels, optimizing conversion funnels, or leading massive GTM strategies, I focus relentlessly on ROI and customer lifetime value.

Let's connect and discuss the future of digital marketing."""
        connection_message = f"Hi [Name],\n\nI loved [Company]'s recent marketing campaign! As a {role} focused on {skill1}, I'm always looking to network with innovative brand builders.\n\nBest,\n{extracted_name}"
        recruiter_message = f"Hi [Recruiter's Name],\n\nI noticed you recruit marketing talent at [Company]. I'm a {role} who specializes in {skill1} and {skill2}. I recently led an initiative resulting in {short_achieve}, and I'm looking for a fast-paced growth team to join.\n\nWould love to connect,\n{extracted_name}"
        tips.extend(["Upload slide decks or case studies showing campaign ROI in the Featured section.", "Endorsements for specific tools (e.g., HubSpot, Google Ads) matter heavily in this domain."])

    elif domain == 'sales':
        headline = f"{role} | Accelerating Revenue & Closing Enterprise Deals | {short_achieve}"
        about = f"""Relentless {role} with a proven history of crushing quotas and expanding market share.

🤝 Core Skills: {skill1}, {skill2}, {skill3}
💰 Top Attainment: {achievement_text}

I specialize in full-cycle sales, complex enterprise negotiations, and building high-trust relationships with key stakeholders. I don't just sell software; I sell strategic solutions that solve massive business problems.

Open to networking with sales leaders and high-performers!"""
        connection_message = f"Hi [Name],\n\nI've been keeping an eye on [Company]'s impressive market expansion. As a {role} driving revenue via {skill1}, I love connecting with elite sales professionals.\n\nBest,\n{extracted_name}"
        recruiter_message = f"Hi [Recruiter's Name],\n\nI see you hire revenue talent for [Company]. I'm a quota-crushing {role} with a track record in {skill1}. Recently, I achieved {short_achieve}. I'm currently looking for a high-growth org to scale with.\n\nLet's connect!\n\nBest,\n{extracted_name}"
        tips.extend(["In your Experience section, put your Quota Attainment % on the very first line of every job.", "Highlight deal sizes and sales cycles (e.g., 'Closed $100k ACV deals')."])

    elif domain == 'finance':
        headline = f"{role} | Strategic Financial Planning & Analysis | {short_achieve}"
        about = f"""Detail-oriented {role} dedicated to protecting margins, ensuring compliance, and driving fiscal growth.

📊 Expertise: {skill1}, {skill2}, {skill3}
📈 Key Impact: {achievement_text}

I translate complex financial models into clear executive insights. I excel at risk mitigation, forecasting accuracy, and streamlining financial operations to save time and capital.

Let's connect to discuss financial strategy and market trends."""
        connection_message = f"Hi [Name],\n\nI was researching [Company] and was impressed by your recent fiscal growth. As a {role} utilizing {skill1}, I am always eager to network with leading finance professionals.\n\nBest,\n{extracted_name}"
        recruiter_message = f"Hi [Recruiter's Name],\n\nI noticed you place finance talent at [Company]. I'm a {role} specializing in {skill1}. I recently drove impact by {short_achieve} and am looking for my next strategic role.\n\nWould love to connect,\n{extracted_name}"
        tips.extend(["Ensure you highlight specific ERP systems (e.g., SAP, Oracle) or financial modeling software in your skills.", "Use metrics related to cost-savings and budget optimization."])

    elif domain == 'hr':
        headline = f"{role} | Cultivating High-Performance Teams | {short_achieve}"
        about = f"""Empathetic {role} passionate about organizational design, talent retention, and company culture.

🤝 Specialties: {skill1}, {skill2}, {skill3}
🌟 Major Win: {achievement_text}

I believe a company's greatest asset is its people. I specialize in building equitable hiring pipelines, streamlining onboarding, and resolving complex employee relations to foster a thriving workplace.

Always open to networking with People Ops and Talent leaders!"""
        connection_message = f"Hi [Name],\n\nI really admire the workplace culture you've built at [Company]. As a {role} focused on {skill1}, I'm always looking to connect with innovative HR leaders.\n\nBest,\n{extracted_name}"
        recruiter_message = f"Hi [Recruiter's Name],\n\nI see you're looking for People Ops talent for [Company]. As a {role} experienced in {skill1}, I recently drove success by {short_achieve}. I'm looking for an org that values culture and growth.\n\nLet's connect!\n\nBest,\n{extracted_name}"
        tips.extend(["Share articles or posts about diversity, equity, and company culture.", "Highlight metrics related to employee retention rates or time-to-hire improvements."])

    else:
        headline = f"{role} | Strategy & Execution | {skill1} & {skill2} | {short_achieve}"
        about = f"""Results-driven {role} with proven expertise in {skill1}, {skill2}, and {skill3}.

🏆 Key Achievement: {achievement_text}

I bring a data-driven mindset and collaborative approach to every challenge — translating complex problems into strategic solutions that move the needle.

Currently open to forward-thinking opportunities where I can leverage my skills to drive growth and innovation.

📩 Let's connect and explore how I can add value to your team!"""
        connection_message = f"Hi [Name],\n\nI came across your profile and was impressed by your work at [Company]. As a {role} specializing in {skill1} and {skill2}, I'd love to connect and exchange insights.\n\nBest,\n{extracted_name}"
        recruiter_message = f"Hi [Recruiter's Name],\n\nI noticed you recruit for {role} talent at [Company]. I'm currently exploring new opportunities and believe my background in {skill1} and {skill2} (recently {short_achieve}), could be a strong fit for your team.\n\nWould love to connect!\n\nBest,\n{extracted_name}"
        tips.extend(["Add a professional profile photo — profiles with photos get 21x more views.", "Follow companies you want to work for and engage with their posts."])

    tips.append("💡 Final Polish: Ensure your 'Open to Work' settings are configured correctly for recruiters only, or publicly if actively unemployed.")

    return {
        'headline': headline,
        'about': about,
        'connection_message': connection_message,
        'recruiter_message': recruiter_message,
        'tips': tips,
        'keywords': [role, skill1, skill2, skill3]
    }


# ────────────────────────────────────────────
# CAREER RECOVERY AGENT
# ────────────────────────────────────────────
def generate_recovery_plan(role, skills, ats_score, portfolio_status, interview_feedback):
    role_str = role if role else 'Professional'
    
    # 1. Diagnostics (Root Cause Analysis)
    diagnostics = []
    
    # Analyze ATS
    ats = ats_score.lower() if ats_score else ''
    if ats in ['low', 'poor', 'needs work', '< 60%']:
        diagnostics.append({"area": "Resume / ATS Compatibility", "issue": "Your resume is likely being filtered out before human review.", "severity": "High"})
    elif ats in ['medium', 'fair', '60-80%']:
        diagnostics.append({"area": "Resume / ATS Compatibility", "issue": "Your resume passes some filters but may lack role-specific keywords.", "severity": "Medium"})
    
    # Analyze Portfolio
    port = portfolio_status.lower() if portfolio_status else ''
    if 'none' in port or 'weak' in port or 'no' in port:
        diagnostics.append({"area": "Proof of Work (Portfolio)", "issue": "Lack of demonstrable projects makes it hard to stand out in a competitive market.", "severity": "High"})
    elif 'outdated' in port:
        diagnostics.append({"area": "Proof of Work (Portfolio)", "issue": "Your portfolio isn't reflecting your current skill level.", "severity": "Medium"})

    # Analyze Interview Feedback
    iv = interview_feedback.lower() if interview_feedback else ''
    if 'ghosted' in iv or 'no response' in iv:
        diagnostics.append({"area": "Application Strategy", "issue": "Cold applying is yielding low conversion. Need a referral/networking strategy.", "severity": "High"})
    elif 'technical' in iv:
        diagnostics.append({"area": "Technical Interviews", "issue": "Falling short on technical assessments or live coding.", "severity": "High"})
    elif 'behavioral' in iv or 'culture' in iv:
        diagnostics.append({"area": "Behavioral Interviews", "issue": "Struggling to communicate soft skills or cultural fit (STAR method).", "severity": "High"})
    
    # Fallback diagnostic if everything seems "okay" but no offers
    if not diagnostics:
        diagnostics.append({"area": "Market Positioning", "issue": "You are likely blending in with the masses. You need a unique value proposition.", "severity": "Medium"})

    # 2. Action Plan Steps
    action_plan = []
    
    # Step 1
    if any(d['area'] == 'Resume / ATS Compatibility' for d in diagnostics):
        action_plan.append({
            "phase": "Phase 1: Stop the Bleeding (Resume Fix)",
            "description": "Halt mass applications. Your resume is the bottleneck.",
            "tactics": [
                "Use the OmniPath Resume Optimizer to inject missing keywords.",
                "Quantify at least 3 bullets per role (e.g., 'Improved X by Y%').",
                "Ensure standard formatting (no columns, standard fonts) for ATS."
            ]
        })
    else:
        action_plan.append({
            "phase": "Phase 1: Shift to Targeted Outreach",
            "description": "Since your resume is okay, cold applying isn't working.",
            "tactics": [
                "Identify 10 high-priority target companies.",
                "Use the LinkedIn Optimizer to craft connection messages to recruiters.",
                "Seek referrals instead of applying via generic portals."
            ]
        })

    # Step 2
    if any(d['area'] == 'Proof of Work (Portfolio)' for d in diagnostics):
        action_plan.append({
            "phase": "Phase 2: Build a Magnet Project",
            "description": "Create undeniable proof of your skills.",
            "tactics": [
                "Use the Portfolio Builder to generate a capstone project idea.",
                "Deploy the project live (GitHub Pages, Vercel, Heroku).",
                "Write a detailed case study (README) explaining the business value."
            ]
        })
    elif any(d['area'] == 'Technical Interviews' for d in diagnostics):
         action_plan.append({
            "phase": "Phase 2: Technical Bootcamp",
            "description": "Sharpen your technical delivery.",
            "tactics": [
                "Practice on LeetCode/HackerRank or build mini-projects.",
                "Do mock technical interviews with a peer.",
                "Focus on explaining your thought process out loud."
            ]
        })
    else:
        action_plan.append({
            "phase": "Phase 2: Personal Branding",
            "description": "Increase inbound opportunities.",
            "tactics": [
                "Post weekly on LinkedIn about your industry insights.",
                "Engage with hiring managers' posts.",
                "Ensure your GitHub/Portfolio is linked prominently."
            ]
        })

    # Step 3
    if any(d['area'] == 'Behavioral Interviews' for d in diagnostics) or any(d['area'] == 'Application Strategy' for d in diagnostics):
        action_plan.append({
            "phase": "Phase 3: Interview Mastery",
            "description": "Convert interviews into offers.",
            "tactics": [
                "Draft 5 core stories using the STAR framework.",
                "Use the OmniPath Interview Coach for mock behavioral sessions.",
                "Prepare insightful questions to ask the interviewers at the end."
            ]
        })
    else:
        action_plan.append({
            "phase": "Phase 3: Deep Market Alignment",
            "description": "Ensure your skills match market demand.",
            "tactics": [
                "Use the Skill Gap Analyzer to find missing secondary skills.",
                "Take a weekend course to patch any obvious holes.",
                "Iterate and start applying again with the upgraded profile."
            ]
        })

    # 3. Immediate Next Steps
    immediate_steps = [
        "Pause all 'Easy Apply' applications immediately.",
        "Pick ONE tactic from Phase 1 and execute it today.",
        "Schedule a 30-min block tomorrow for Phase 2 planning."
    ]

    return {
        "role": role_str,
        "diagnostics": diagnostics,
        "action_plan": action_plan,
        "immediate_steps": immediate_steps
    }
