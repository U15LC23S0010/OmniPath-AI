import time
import datetime
import uuid
import json
from legacy_agents import (
    analyze_resume, debate_resume, analyze_skill_gap, generate_roadmap,
    generate_portfolio, optimize_linkedin, generate_recovery_plan,
    get_interview_question, evaluate_answer, generate_career_plan,
    match_jobs, get_salary_data
)

class SharedMemory:
    def __init__(self, session_data=None):
        if not session_data:
            session_data = {}
        self.session_id = session_data.get('session_id', str(uuid.uuid4()))
        self.timestamp = session_data.get('timestamp', datetime.datetime.now().isoformat())
        
        # User details
        self.profile = session_data.get('profile', {})
        
        # Agent Outputs
        self.resume_data = session_data.get('resume_data', {})
        self.ats_score = session_data.get('ats_score', None)
        self.skill_gaps = session_data.get('skill_gaps', {})
        self.learning_roadmap = session_data.get('learning_roadmap', {})
        self.portfolio_output = session_data.get('portfolio_output', {})
        self.interview_history = session_data.get('interview_history', [])
        self.job_matches = session_data.get('job_matches', [])
        self.salary_report = session_data.get('salary_report', {})
        self.linkedin_optimization = session_data.get('linkedin_optimization', {})
        self.career_recovery_plan = session_data.get('career_recovery_plan', {})
        
        # System State
        self.current_task = session_data.get('current_task', None)
        self.active_agent = session_data.get('active_agent', None)
        self.execution_history = session_data.get('execution_history', [])

    def log(self, message):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.execution_history.append(f"[{ts}] {message}")

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'profile': self.profile,
            'resume_data': self.resume_data,
            'ats_score': self.ats_score,
            'skill_gaps': self.skill_gaps,
            'learning_roadmap': self.learning_roadmap,
            'portfolio_output': self.portfolio_output,
            'interview_history': self.interview_history,
            'job_matches': self.job_matches,
            'salary_report': self.salary_report,
            'linkedin_optimization': self.linkedin_optimization,
            'career_recovery_plan': self.career_recovery_plan,
            'current_task': self.current_task,
            'active_agent': self.active_agent,
            'execution_history': self.execution_history[-100:] # Cap history
        }

class BaseAgent:
    def __init__(self):
        self.name = "Base Agent"
        self.description = "Base agent description"
        self.supported_tasks = []
        self.status = "idle"

    def execute(self, shared_memory, **kwargs):
        raise NotImplementedError

class ResumeOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Resume Optimizer Agent"
        self.description = "Optimizes resume and provides debate feedback."
        self.supported_tasks = ["debate_resume"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        text = kwargs.get('text', '')
        role = kwargs.get('role', shared_memory.profile.get('role', ''))
        result = debate_resume(text, role)
        
        shared_memory.resume_data['debate'] = result
        
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class ATSAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "ATS Analyzer Agent"
        self.description = "Analyzes resume for ATS compatibility."
        self.supported_tasks = ["analyze_resume"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        text = kwargs.get('text', '')
        role = kwargs.get('role', shared_memory.profile.get('role', ''))
        result = analyze_resume(text, role)
        
        shared_memory.resume_data['ats_analysis'] = result
        if 'ats_score' in result:
            shared_memory.ats_score = result['ats_score']
            
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class SkillGapAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Skill Gap Agent"
        self.description = "Analyzes skill gaps against target roles."
        self.supported_tasks = ["analyze_skill_gap"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        role = kwargs.get('role', shared_memory.profile.get('role', 'Professional'))
        skills = kwargs.get('skills', shared_memory.profile.get('skills', ''))
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]
            
        result = analyze_skill_gap(role, skills)
        shared_memory.skill_gaps = result
        
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class LearningRoadmapAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Learning Roadmap Agent"
        self.description = "Generates a customized learning roadmap."
        self.supported_tasks = ["generate_roadmap"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        role = kwargs.get('role', shared_memory.profile.get('role', 'Professional'))
        timeline = kwargs.get('timeline', '6')
        result = generate_roadmap(role, timeline)
        
        shared_memory.learning_roadmap = result
        
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class PortfolioGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Portfolio Generator Agent"
        self.description = "Generates portfolio projects tailored to the user."
        self.supported_tasks = ["generate_portfolio"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        role = kwargs.get('role', shared_memory.profile.get('role', 'Professional'))
        difficulty = kwargs.get('difficulty', 'intermediate')
        result = generate_portfolio(role, difficulty)
        
        shared_memory.portfolio_output = result
        
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class InterviewCoachAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Interview Coach Agent"
        self.description = "Provides interview questions and evaluates answers."
        self.supported_tasks = ["get_interview_question", "evaluate_answer"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        task = kwargs.get('task')
        if task == "get_interview_question":
            role = kwargs.get('role', shared_memory.profile.get('role', 'Professional'))
            q_type = kwargs.get('type', 'behavioral')
            q_num = kwargs.get('question_num', 1)
            experience = kwargs.get('experience', shared_memory.profile.get('experience', 'mid'))
            result = get_interview_question(role, q_type, q_num, experience)
            shared_memory.interview_history.append({"type": "question", "data": result})
        elif task == "evaluate_answer":
            question = kwargs.get('question', '')
            answer = kwargs.get('answer', '')
            result = evaluate_answer(question, answer)
            shared_memory.interview_history.append({"type": "evaluation", "question": question, "answer": answer, "data": result})
        else:
            result = {"error": "Invalid task"}
            
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class JobMatchingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Job Matching Agent"
        self.description = "Matches jobs based on resume and criteria."
        self.supported_tasks = ["match_jobs"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        role = kwargs.get('role', shared_memory.profile.get('role', 'Professional'))
        remote = kwargs.get('remote', 'any')
        salary_min = kwargs.get('salary_min', '0')
        resume_text = kwargs.get('resume_text', '')
        result = match_jobs(role, remote, salary_min, resume_text)
        
        shared_memory.job_matches = result.get('jobs', [])
        
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class SalaryIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Salary Intelligence Agent"
        self.description = "Provides salary intelligence data."
        self.supported_tasks = ["get_salary_data"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        role = kwargs.get('role', shared_memory.profile.get('role', ''))
        country = kwargs.get('country', shared_memory.profile.get('country', 'us'))
        state = kwargs.get('state', '')
        experience = kwargs.get('experience', 0)
        result = get_salary_data(role, country, state, experience)
        
        shared_memory.salary_report = result
        
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class LinkedInOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "LinkedIn Optimizer Agent"
        self.description = "Optimizes LinkedIn profile data."
        self.supported_tasks = ["optimize_linkedin"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        role = kwargs.get('role', shared_memory.profile.get('role', ''))
        url = kwargs.get('url', '')
        skills_input = kwargs.get('skills', shared_memory.profile.get('skills', ''))
        achievement = kwargs.get('achievement', shared_memory.profile.get('achievement', ''))
        
        result = optimize_linkedin(role, url, skills_input, achievement)
        shared_memory.linkedin_optimization = result
        
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class CareerRecoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Career Recovery Agent"
        self.description = "Generates a recovery plan for career setbacks."
        self.supported_tasks = ["generate_recovery_plan"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        role = kwargs.get('role', shared_memory.profile.get('role', ''))
        skills_input = kwargs.get('skills', shared_memory.profile.get('skills', ''))
        
        # Collaborate using shared memory
        ats_score = kwargs.get('ats_score', str(shared_memory.ats_score or ''))
        
        portfolio_status = kwargs.get('portfolio_status', '')
        if not portfolio_status:
            portfolio_status = "Has generated projects" if shared_memory.portfolio_output else "No portfolio"
            
        interview_feedback = kwargs.get('interview_feedback', '')
        if not interview_feedback and shared_memory.interview_history:
            interview_feedback = "Practiced interviews recently"

        result = generate_recovery_plan(role, skills_input, ats_score, portfolio_status, interview_feedback)
        shared_memory.career_recovery_plan = result
        
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result

class CareerPlanAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "Career Plan Agent"
        self.description = "Generates high level career plans based on interests."
        self.supported_tasks = ["generate_career_plan"]

    def execute(self, shared_memory, **kwargs):
        self.status = "running"
        shared_memory.active_agent = self.name
        start_time = time.time()
        shared_memory.log(f"{self.name} started.")
        
        interests = kwargs.get('interests', [])
        result = generate_career_plan(interests)
        
        shared_memory.profile['career_plan'] = result
        
        exec_time = time.time() - start_time
        self.status = "idle"
        shared_memory.active_agent = None
        shared_memory.log(f"{self.name} completed in {exec_time:.2f}s.")
        return result


class AgentRegistry:
    def __init__(self):
        self._agents = {}
        self._register_all()

    def _register_all(self):
        agents = [
            ResumeOptimizerAgent(),
            ATSAnalyzerAgent(),
            SkillGapAgent(),
            LearningRoadmapAgent(),
            PortfolioGeneratorAgent(),
            InterviewCoachAgent(),
            JobMatchingAgent(),
            SalaryIntelligenceAgent(),
            LinkedInOptimizerAgent(),
            CareerRecoveryAgent(),
            CareerPlanAgent()
        ]
        for agent in agents:
            for task in agent.supported_tasks:
                self._agents[task] = agent
                
    def get_agent(self, task):
        return self._agents.get(task)

    def list_agents(self):
        # Return unique agents
        unique = {id(a): a for a in self._agents.values()}
        return list(unique.values())

    def agent_status(self):
        return [{"name": a.name, "status": a.status} for a in self.list_agents()]


class CareerOrchestrator:
    def __init__(self):
        self.registry = AgentRegistry()
        self.system_start_time = time.time()
        self.total_requests = 0
        self.execution_times = []
        self.running_tasks = []
        self.completed_tasks = []

    def execute_task(self, shared_memory, task_name, **kwargs):
        self.total_requests += 1
        shared_memory.log(f"Career Orchestrator received task: {task_name}")
        self.running_tasks.append(task_name)
        shared_memory.current_task = task_name
        
        agent = self.registry.get_agent(task_name)
        if not agent:
            shared_memory.log(f"No agent found for task: {task_name}")
            self.running_tasks.remove(task_name)
            shared_memory.current_task = None
            return {"error": "Task not supported by any agent"}

        start_time = time.time()
        try:
            result = agent.execute(shared_memory, **kwargs)
            self.completed_tasks.append(task_name)
        except Exception as e:
            import traceback
            traceback.print_exc()
            shared_memory.log(f"Error executing {task_name} via {agent.name}: {str(e)}")
            result = {"error": str(e)}
        finally:
            if task_name in self.running_tasks:
                self.running_tasks.remove(task_name)
            shared_memory.current_task = None
            
            exec_time = time.time() - start_time
            self.execution_times.append(exec_time)
            
        shared_memory.log(f"Response returned.")
        return result

    def get_status(self, shared_memory):
        avg_exec_time = sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
        uptime = time.time() - self.system_start_time
        
        sm_json = json.dumps(shared_memory.to_dict())
        memory_size = len(sm_json.encode('utf-8'))
        
        return {
            'system_health': 'Healthy',
            'current_agent': shared_memory.active_agent,
            'running_tasks': self.running_tasks,
            'completed_tasks': self.completed_tasks,
            'avg_execution_time_ms': round(avg_exec_time * 1000, 2),
            'total_requests': self.total_requests,
            'memory_size_bytes': memory_size,
            'system_uptime_s': round(uptime, 2),
            'agent_status': self.registry.agent_status()
        }
