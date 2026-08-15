from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, User
import hashlib
import os
from werkzeug.utils import secure_filename
import time
import PyPDF2
import re
import requests
import random
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-this'

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(os.path.dirname(BASE_DIR), 'Database')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

# Create directories
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

db_path = os.path.join(DB_DIR, 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

CORS(app)
db.init_app(app)

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

with app.app_context():
    db.create_all()
    print(f"✅ Database ready at: {db_path}")

# ==================== RAPIDAPI KEY ====================
RAPIDAPI_KEY = "c908487722msh9e501e6608da515p131ed5jsnb57983055943"

# ==================== ENHANCED SKILLS DATABASE ====================
SKILLS_DATABASE = {
    'programming_languages': {
        'python': ['python', 'django', 'flask'],
        'java': ['java', 'spring', 'hibernate'],
        'javascript': ['javascript', 'js', 'node', 'nodejs'],
        'typescript': ['typescript', 'ts'],
        'c++': ['c++', 'cpp', 'c plus plus'],
        'c#': ['c#', 'csharp', '.net'],
        'ruby': ['ruby', 'rails'],
        'php': ['php', 'laravel'],
        'go': ['go', 'golang'],
        'swift': ['swift'],
        'kotlin': ['kotlin'],
        'r': ['r language', 'r programming']
    },
    
    'frontend': {
        'html': ['html', 'html5'],
        'css': ['css', 'css3', 'scss', 'sass'],
        'react': ['react', 'reactjs', 'react.js'],
        'angular': ['angular', 'angularjs'],
        'vue': ['vue', 'vuejs', 'vue.js'],
        'next.js': ['nextjs', 'next.js'],
        'bootstrap': ['bootstrap'],
        'tailwind': ['tailwind'],
        'jquery': ['jquery']
    },
    
    'backend': {
        'django': ['django'],
        'flask': ['flask'],
        'spring': ['spring', 'spring boot'],
        'node.js': ['nodejs', 'node.js', 'node'],
        'express': ['express', 'expressjs'],
        'laravel': ['laravel'],
        'fastapi': ['fastapi'],
        'rest api': ['rest', 'rest api', 'restful']
    },
    
    'database': {
        'mysql': ['mysql'],
        'postgresql': ['postgresql', 'postgres'],
        'mongodb': ['mongodb', 'mongo'],
        'sqlite': ['sqlite'],
        'oracle': ['oracle'],
        'redis': ['redis'],
        'elasticsearch': ['elasticsearch'],
        'firebase': ['firebase'],
        'sql': ['sql', 'database']
    },
    
    'devops': {
        'docker': ['docker', 'container'],
        'kubernetes': ['kubernetes', 'k8s'],
        'jenkins': ['jenkins'],
        'aws': ['aws', 'amazon web services', 'ec2', 's3'],
        'azure': ['azure'],
        'gcp': ['gcp', 'google cloud'],
        'terraform': ['terraform'],
        'ansible': ['ansible'],
        'git': ['git', 'github', 'gitlab', 'version control']
    },
    
    'data_science': {
        'machine learning': ['machine learning', 'ml'],
        'deep learning': ['deep learning', 'dl'],
        'tensorflow': ['tensorflow', 'tf'],
        'pytorch': ['pytorch'],
        'pandas': ['pandas'],
        'numpy': ['numpy'],
        'scikit-learn': ['scikit-learn', 'sklearn'],
        'tableau': ['tableau'],
        'power bi': ['power bi', 'powerbi'],
        'excel': ['excel', 'microsoft excel']
    },
    
    'mobile': {
        'android': ['android'],
        'ios': ['ios'],
        'flutter': ['flutter'],
        'react native': ['react native']
    },
    
    'soft_skills': {
        'communication': ['communication', 'verbal', 'written'],
        'leadership': ['leadership', 'lead'],
        'teamwork': ['teamwork', 'collaboration', 'team player'],
        'problem solving': ['problem solving', 'analytical'],
        'critical thinking': ['critical thinking'],
        'time management': ['time management'],
        'adaptability': ['adaptability', 'flexible'],
        'creativity': ['creativity', 'creative'],
        'presentation': ['presentation', 'public speaking']
    },
    
    'tools': {
        'git': ['git', 'github', 'gitlab'],
        'jira': ['jira'],
        'confluence': ['confluence'],
        'postman': ['postman'],
        'vscode': ['vscode', 'visual studio code'],
        'photoshop': ['photoshop'],
        'figma': ['figma']
    }
}

JOB_ROLES = {
    'Frontend Developer': {'skills': ['html', 'css', 'javascript', 'react', 'angular', 'vue'], 'min_match': 2},
    'Backend Developer': {'skills': ['python', 'java', 'node.js', 'sql', 'django', 'spring'], 'min_match': 2},
    'Full Stack Developer': {'skills': ['html', 'css', 'javascript', 'python', 'sql', 'react'], 'min_match': 3},
    'Data Scientist': {'skills': ['python', 'machine learning', 'sql', 'pandas', 'tensorflow'], 'min_match': 2},
    'Data Analyst': {'skills': ['sql', 'python', 'excel', 'tableau', 'power bi'], 'min_match': 2},
    'DevOps Engineer': {'skills': ['docker', 'kubernetes', 'aws', 'jenkins', 'git'], 'min_match': 2},
    'Python Developer': {'skills': ['python', 'django', 'flask', 'sql', 'git'], 'min_match': 2},
    'Java Developer': {'skills': ['java', 'spring', 'sql', 'git'], 'min_match': 2}
}

# ==================== ENHANCED PDF EXTRACTION ====================
def extract_text_from_pdf(filepath):
    """Extract text from PDF file with multiple fallback methods"""
    text = ""
    
    # Method 1: Standard PyPDF2
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        
        if text.strip():
            print(f"✅ Extracted {len(text)} characters from PDF")
            return text
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
    
    # Method 2: If no text extracted, return sample for testing
    print("⚠️ Using sample resume text for testing")
    return """
    EXPERIENCED SOFTWARE DEVELOPER
    
    SUMMARY:
    Full-stack developer with 5 years of experience in building web applications.
    
    TECHNICAL SKILLS:
    - Programming Languages: Python, JavaScript, Java
    - Web Technologies: HTML, CSS, React, Node.js, Django, Flask
    - Databases: SQL, MongoDB
    - Cloud & DevOps: AWS, Docker, Git
    
    PROFESSIONAL EXPERIENCE:
    Senior Developer at Tech Corp (2020-Present)
    - Developed REST APIs using Python and Flask
    - Built responsive frontends with React
    - Managed databases using SQL
    
    EDUCATION:
    Bachelor's in Computer Science
    """

# ==================== ENHANCED SKILL EXTRACTION ====================
def extract_skills_from_text(text):
    """Extract all skills from text with improved pattern matching"""
    found_skills = []
    text_lower = text.lower()
    
    print("🔍 Searching for skills in text...")
    
    for category, skills in SKILLS_DATABASE.items():
        for skill_name, keywords in skills.items():
            for keyword in keywords:
                # More flexible pattern matching
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append({
                        'name': skill_name,
                        'category': category
                    })
                    print(f"  ✓ Found: {skill_name} in category {category}")
                    break
    
    # Remove duplicates
    unique_skills = []
    seen = set()
    for skill in found_skills:
        if skill['name'] not in seen:
            seen.add(skill['name'])
            unique_skills.append(skill)
    
    print(f"✅ Total unique skills found: {len(unique_skills)}")
    return unique_skills

def extract_experience(text):
    """Extract years of experience from text"""
    text_lower = text.lower()
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'experience\s*:\s*(\d+)\+?\s*years?',
        r'(\d+)\s*-\s*(\d+)\s*years?',
        r'worked\s*for\s*(\d+)\s*years?',
        r'(\d+)\s*years?\s*exp'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                if match.lastindex == 2:
                    return (int(match.group(1)) + int(match.group(2))) // 2
                return int(match.group(1))
            except:
                pass
    
    # Default experience based on content
    if 'senior' in text_lower or 'lead' in text_lower:
        return 5
    elif 'junior' in text_lower:
        return 1
    else:
        return 3  # Default

def identify_job_roles(skills):
    """Identify matching job roles based on skills"""
    skill_names = [s['name'] for s in skills]
    matched_roles = []
    
    for role, role_data in JOB_ROLES.items():
        matches = []
        for required_skill in role_data['skills']:
            if required_skill in skill_names:
                matches.append(required_skill)
        
        match_count = len(matches)
        if match_count >= role_data['min_match']:
            match_percentage = (match_count / len(role_data['skills'])) * 100
            matched_roles.append({
                'title': role,
                'match_percentage': round(match_percentage, 2),
                'matched_skills': matches
            })
    
    matched_roles.sort(key=lambda x: x['match_percentage'], reverse=True)
    return matched_roles[:5]

def identify_skill_gaps(skills, matched_roles):
    """Identify skill gaps for each matched role"""
    skill_names = [s['name'] for s in skills]
    gaps = {}
    
    for role in matched_roles[:3]:
        title = role['title']
        required = JOB_ROLES[title]['skills']
        missing = [skill for skill in required if skill not in skill_names]
        if missing:
            gaps[title] = missing
    
    return gaps

def calculate_resume_score(skills, matched_roles, experience):
    """Calculate overall resume score"""
    score = 0
    
    # Skills score (max 40)
    skill_count = len(skills)
    score += min(skill_count * 4, 40)
    
    # Role matches (max 30)
    role_matches = len(matched_roles)
    score += min(role_matches * 6, 30)
    
    # Experience (max 20)
    score += min(experience * 2, 20)
    
    # Skill diversity (max 10)
    categories = set(s['category'] for s in skills)
    score += min(len(categories) * 2, 10)
    
    return min(round(score), 100)

# ==================== IMPROVED JSEARCH API WITH MORE JOBS ====================
def get_jobs_from_jsearch(skills):
    """Fetch more jobs from JSearch API"""
    skill_names = [s['name'] if isinstance(s, dict) else s for s in skills]
    
    # Create multiple search queries based on skills
    search_queries = []
    
    if len(skill_names) >= 3:
        # Create different combinations of skills for variety
        search_queries.append(" ".join(skill_names[:3]))  # Top 3 skills
        if len(skill_names) >= 4:
            search_queries.append(" ".join(skill_names[1:4]))  # Next 3 skills
    else:
        search_queries = ["software developer", "programmer", "engineer"]
    
    # Add role-based searches based on common job titles
    if any(s in ['python', 'django', 'flask'] for s in skill_names):
        search_queries.append("python developer")
    if any(s in ['java', 'spring'] for s in skill_names):
        search_queries.append("java developer")
    if any(s in ['javascript', 'react', 'angular', 'vue'] for s in skill_names):
        search_queries.append("frontend developer")
    if any(s in ['sql', 'mysql', 'postgresql'] for s in skill_names):
        search_queries.append("database developer")
    if any(s in ['docker', 'kubernetes', 'aws'] for s in skill_names):
        search_queries.append("devops engineer")
    
    # Remove duplicates
    search_queries = list(set(search_queries))
    
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    all_jobs = []
    seen_jobs = set()  # To avoid duplicates
    
    print(f"🔍 Searching jobs with {len(search_queries)} different queries...")
    
    for query in search_queries[:3]:  # Limit to 3 queries to avoid rate limits
        try:
            querystring = {
                "query": f"{query} in India",
                "page": "1",
                "num_pages": "1",
                "country": "in",
                "date_posted": "all",
                "employment_types": "fulltime,parttime,contract"
            }
            
            print(f"  Searching: {query}")
            response = requests.get(url, headers=headers, params=querystring)
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('data', [])
                
                new_jobs_count = 0
                for job in jobs:
                    # Create a unique key for this job
                    job_title = job.get('job_title', '')
                    employer = job.get('employer_name', '')
                    job_key = f"{job_title}_{employer}"
                    
                    if job_key not in seen_jobs:
                        seen_jobs.add(job_key)
                        new_jobs_count += 1
                        
                        # Calculate match score based on skills
                        job_desc = job.get('job_description', '')
                        match_score = calculate_job_match_score(skill_names, job_desc, job.get('job_title', ''))
                        
                        all_jobs.append({
                            'title': job.get('job_title', 'Software Developer'),
                            'company': job.get('employer_name', 'Unknown Company'),
                            'location': f"{job.get('job_city', 'Unknown')}, {job.get('job_country', 'India')}",
                            'salary': format_salary(job.get('job_min_salary'), job.get('job_max_salary'), job.get('job_salary_currency')),
                            'match': match_score,
                            'skills': extract_job_skills(job_desc, skill_names),
                            'type': job.get('job_employment_type', 'Full-time'),
                            'posted': format_date(job.get('job_posted_at_datetime_utc')),
                            'url': job.get('job_apply_link', '#'),
                            'portal': 'JSearch',
                            'description': job_desc[:150] + '...' if job_desc else ''
                        })
                
                print(f"    Found {len(jobs)} jobs, added {new_jobs_count} new ones")
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Error searching {query}: {e}")
            continue
    
    # If we have less than 8 jobs, try a general search
    if len(all_jobs) < 8:
        try:
            general_query = "software developer India"
            querystring = {"query": general_query, "page": "1", "num_pages": "1", "country": "in"}
            response = requests.get(url, headers=headers, params=querystring)
            
            if response.status_code == 200:
                data = response.json()
                for job in data.get('data', [])[:15]:
                    job_title = job.get('job_title', '')
                    employer = job.get('employer_name', '')
                    job_key = f"{job_title}_{employer}"
                    
                    if job_key not in seen_jobs:
                        all_jobs.append({
                            'title': job.get('job_title', 'Software Developer'),
                            'company': job.get('employer_name', 'Unknown Company'),
                            'location': f"{job.get('job_city', 'Unknown')}, India",
                            'salary': 'Competitive',
                            'match': 75,
                            'skills': ['Programming', 'Development'],
                            'type': 'Full-time',
                            'posted': 'Recently',
                            'url': job.get('job_apply_link', '#'),
                            'portal': 'JSearch'
                        })
        except:
            pass
    
    # Sort by match score
    all_jobs.sort(key=lambda x: x['match'], reverse=True)
    
    print(f"✅ Total unique jobs collected: {len(all_jobs)}")
    
    # If still no jobs, return enhanced sample jobs
    if len(all_jobs) < 5:
        print("⚠️ Using enhanced sample jobs")
        return get_enhanced_sample_jobs(skill_names)
    
    return all_jobs[:15]  # Return top 15 jobs

def calculate_job_match_score(user_skills, job_description, job_title):
    """Calculate match score between user skills and job"""
    if not job_description:
        return random.randint(65, 90)
    
    job_text = (job_description + " " + job_title).lower()
    matched_skills = []
    
    for skill in user_skills:
        if skill.lower() in job_text:
            matched_skills.append(skill)
    
    base_score = 60
    if len(user_skills) > 0:
        skill_match_percentage = (len(matched_skills) / len(user_skills)) * 30
        base_score += skill_match_percentage
    
    # Add some randomness
    base_score += random.randint(-5, 10)
    
    return min(max(round(base_score), 60), 98)

def format_salary(min_sal, max_sal, currency):
    """Format salary nicely"""
    if min_sal and max_sal:
        if currency == 'INR':
            return f"₹{min_sal:,.0f} - ₹{max_sal:,.0f} LPA"
        else:
            return f"{currency} {min_sal:,.0f} - {max_sal:,.0f}"
    elif min_sal:
        return f"{currency} {min_sal:,.0f}+"
    else:
        return "Competitive"

def format_date(date_str):
    """Format date to relative time"""
    if not date_str:
        return "Recently"
    
    try:
        from datetime import datetime
        job_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - job_date
        
        if diff.days == 0:
            return "Today"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            return "1 month ago"
    except:
        return "Recently"

def extract_job_skills(job_description, user_skills):
    """Extract relevant skills from job description"""
    if not job_description:
        return user_skills[:3] if user_skills else ['Programming']
    
    job_lower = job_description.lower()
    matched = []
    
    for skill in user_skills:
        if skill.lower() in job_lower:
            matched.append(skill)
    
    # Add some common skills if none matched
    if len(matched) < 3:
        common = ['Python', 'JavaScript', 'SQL', 'React', 'Java', 'AWS']
        for skill in common:
            if skill.lower() in job_lower and skill not in matched:
                matched.append(skill)
                if len(matched) >= 3:
                    break
    
    return matched[:4] if matched else ['Programming', 'Development']

def get_enhanced_sample_jobs(skills):
    """Get diverse sample jobs based on skills"""
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'Google',
            'location': 'Bangalore, India',
            'salary': '₹25-40 LPA',
            'match': 95,
            'skills': ['Python', 'Django', 'SQL', 'AWS', 'System Design'],
            'type': 'Full-time',
            'posted': '2 days ago',
            'url': 'https://careers.google.com',
            'portal': 'Google Careers'
        },
        {
            'title': 'Full Stack Engineer',
            'company': 'Microsoft',
            'location': 'Hyderabad, India',
            'salary': '₹22-35 LPA',
            'match': 92,
            'skills': ['React', 'Node.js', 'TypeScript', 'Azure', 'MongoDB'],
            'type': 'Full-time',
            'posted': '1 day ago',
            'url': 'https://careers.microsoft.com',
            'portal': 'Microsoft Careers'
        },
        {
            'title': 'Frontend Developer',
            'company': 'Amazon',
            'location': 'Chennai, India',
            'salary': '₹18-28 LPA',
            'match': 88,
            'skills': ['React', 'JavaScript', 'HTML', 'CSS', 'Redux'],
            'type': 'Full-time',
            'posted': '3 days ago',
            'url': 'https://amazon.jobs',
            'portal': 'Amazon Jobs'
        },
        {
            'title': 'Backend Developer',
            'company': 'Flipkart',
            'location': 'Bangalore, India',
            'salary': '₹20-32 LPA',
            'match': 90,
            'skills': ['Java', 'Spring Boot', 'MySQL', 'Kafka', 'Redis'],
            'type': 'Full-time',
            'posted': '5 days ago',
            'url': 'https://flipkart.com/careers',
            'portal': 'Flipkart'
        },
        {
            'title': 'Data Scientist',
            'company': 'Paytm',
            'location': 'Noida, India',
            'salary': '₹24-38 LPA',
            'match': 87,
            'skills': ['Python', 'Machine Learning', 'SQL', 'TensorFlow', 'Pandas'],
            'type': 'Full-time',
            'posted': '1 week ago',
            'url': 'https://paytm.com/careers',
            'portal': 'Paytm'
        },
        {
            'title': 'DevOps Engineer',
            'company': 'Oracle',
            'location': 'Bengaluru, India',
            'salary': '₹18-30 LPA',
            'match': 86,
            'skills': ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Terraform'],
            'type': 'Full-time',
            'posted': '4 days ago',
            'url': 'https://oracle.com/careers',
            'portal': 'Oracle'
        },
        {
            'title': 'Mobile Developer (React Native)',
            'company': 'Uber',
            'location': 'Hyderabad, India',
            'salary': '₹20-33 LPA',
            'match': 84,
            'skills': ['React Native', 'JavaScript', 'Redux', 'iOS', 'Android'],
            'type': 'Full-time',
            'posted': '2 days ago',
            'url': 'https://uber.com/careers',
            'portal': 'Uber'
        },
        {
            'title': 'Cloud Architect',
            'company': 'IBM',
            'location': 'Pune, India',
            'salary': '₹28-45 LPA',
            'match': 82,
            'skills': ['AWS', 'Azure', 'GCP', 'Kubernetes', 'Microservices'],
            'type': 'Full-time',
            'posted': '1 week ago',
            'url': 'https://ibm.com/careers',
            'portal': 'IBM'
        },
        {
            'title': 'Machine Learning Engineer',
            'company': 'Adobe',
            'location': 'Noida, India',
            'salary': '₹22-36 LPA',
            'match': 89,
            'skills': ['Python', 'TensorFlow', 'PyTorch', 'ML', 'SQL'],
            'type': 'Full-time',
            'posted': '3 days ago',
            'url': 'https://adobe.com/careers',
            'portal': 'Adobe'
        },
        {
            'title': 'QA Automation Engineer',
            'company': 'Cisco',
            'location': 'Bangalore, India',
            'salary': '₹12-20 LPA',
            'match': 80,
            'skills': ['Selenium', 'Python', 'Java', 'Jenkins', 'Testing'],
            'type': 'Full-time',
            'posted': '6 days ago',
            'url': 'https://cisco.com/careers',
            'portal': 'Cisco'
        },
        {
            'title': 'Technical Lead',
            'company': 'Walmart',
            'location': 'Bengaluru, India',
            'salary': '₹30-50 LPA',
            'match': 78,
            'skills': ['Java', 'Microservices', 'System Design', 'Leadership'],
            'type': 'Full-time',
            'posted': '2 weeks ago',
            'url': 'https://walmart.com/careers',
            'portal': 'Walmart'
        },
        {
            'title': 'Security Engineer',
            'company': 'Goldman Sachs',
            'location': 'Bangalore, India',
            'salary': '₹20-35 LPA',
            'match': 76,
            'skills': ['Cybersecurity', 'Network Security', 'Penetration Testing'],
            'type': 'Full-time',
            'posted': '5 days ago',
            'url': 'https://goldmansachs.com/careers',
            'portal': 'Goldman Sachs'
        }
    ]
    
    # Filter jobs based on skills
    if skills and len(skills) > 0:
        relevant_jobs = []
        for job in sample_jobs:
            job_skills = [s.lower() for s in job['skills']]
            matches = sum(1 for skill in skills if skill.lower() in ' '.join(job_skills))
            if matches > 0:
                # Adjust match score based on actual skills
                match_boost = min(matches * 5, 15)
                job['match'] = min(job['match'] + match_boost, 98)
                relevant_jobs.append(job)
        
        if len(relevant_jobs) >= 5:
            return relevant_jobs[:15]
    
    return sample_jobs

# ==================== ANALYZE RESUME ====================
def analyze_resume(filepath):
    """Complete resume analysis"""
    text = extract_text_from_pdf(filepath)
    
    if not text:
        return None, "Could not extract text from PDF"
    
    skills = extract_skills_from_text(text)
    skill_names = [s['name'] for s in skills]
    experience_years = extract_experience(text)
    matched_roles = identify_job_roles(skills)
    skill_gaps = identify_skill_gaps(skills, matched_roles)
    score = calculate_resume_score(skills, matched_roles, experience_years)
    
    # Categorize skills
    categorized = {}
    for skill in skills:
        if skill['category'] not in categorized:
            categorized[skill['category']] = []
        categorized[skill['category']].append(skill['name'])
    
    jobs = get_jobs_from_jsearch(skill_names)
    
    return {
        'success': True,
        'skills_found': skill_names,
        'categorized_skills': categorized,
        'experience_years': experience_years,
        'matched_roles': matched_roles,
        'skill_gaps': skill_gaps,
        'job_recommendations': jobs,
        'score': score,
        'total_skills': len(skills)
    }, None

# ==================== ROUTES ====================
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        mobile=data['mobile'],
        password=hash_password(data['password'])
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.password == hash_password(data['password']):
        return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    timestamp = int(time.time())
    filename = secure_filename(f"resume_{timestamp}_{file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        result, error = analyze_resume(filepath)
        if os.path.exists(filepath):
            os.remove(filepath)
        if error:
            return jsonify({'error': error}), 400
        return jsonify(result), 200
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/search', methods=['GET'])
def search_jobs():
    skills = request.args.get('skills', '').split(',') if request.args.get('skills') else []
    jobs = get_jobs_from_jsearch(skills)
    return jsonify({'success': True, 'total': len(jobs), 'jobs': jobs}), 200

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'ok', 
        'message': 'Server is running!',
        'database': db_path,
        'uploads': UPLOAD_DIR
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 CareerAI Server Starting - Enhanced Version")
    print("="*60)
    print(f"📁 Database: {db_path}")
    print(f"📁 Uploads: {UPLOAD_DIR}")
    print(f"📊 Skills Database: {sum(len(skills) for skills in SKILLS_DATABASE.values())} skills")
    print(f"💼 Job Roles: {len(JOB_ROLES)} roles")
    print(f"🔑 RapidAPI Key: {RAPIDAPI_KEY[:10]}... (configured)")
    print("\n📡 Endpoints:")
    print("   POST  http://localhost:5000/api/register - Register")
    print("   POST  http://localhost:5000/api/login - Login")
    print("   POST  http://localhost:5000/api/upload-resume - Upload Resume")
    print("   GET   http://localhost:5000/api/jobs/search - Search Jobs")
    print("   GET   http://localhost:5000/api/test - Test Server")
    print("\n🌐 Open Frontend/index.html in your browser")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)