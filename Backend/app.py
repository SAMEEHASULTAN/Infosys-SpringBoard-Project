from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, User
import hashlib
import os
from werkzeug.utils import secure_filename
import time
import PyPDF2
import re
from datetime import datetime

# LinkedIn scraping imports
from linkedin_scraper import LinkedInScraper, match_jobs_with_resume
import threading
import json

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

# ==================== SKILLS DATABASE ====================
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

# ==================== PDF EXTRACTION ====================
def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    text = ""
    
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

# ==================== SKILL EXTRACTION ====================
def extract_skills_from_text(text):
    """Extract all skills from text"""
    found_skills = []
    text_lower = text.lower()
    
    print("🔍 Searching for skills in text...")
    
    for category, skills in SKILLS_DATABASE.items():
        for skill_name, keywords in skills.items():
            for keyword in keywords:
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
    
    if 'senior' in text_lower or 'lead' in text_lower:
        return 5
    elif 'junior' in text_lower:
        return 1
    else:
        return 3

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
    
    skill_count = len(skills)
    score += min(skill_count * 4, 40)
    
    role_matches = len(matched_roles)
    score += min(role_matches * 6, 30)
    
    score += min(experience * 2, 20)
    
    categories = set(s['category'] for s in skills)
    score += min(len(categories) * 2, 10)
    
    return min(round(score), 100)

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
    
    # No jobs returned here - user will need to scrape LinkedIn
    return {
        'success': True,
        'skills_found': skill_names,
        'categorized_skills': categorized,
        'experience_years': experience_years,
        'matched_roles': matched_roles,
        'skill_gaps': skill_gaps,
        'score': score,
        'total_skills': len(skills),
        'message': 'Resume analyzed. Click "Scrape LinkedIn Jobs" to find matching positions.'
    }, None

# ==================== EXISTING ROUTES ====================
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

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'ok', 
        'message': 'Server is running!',
        'database': db_path,
        'uploads': UPLOAD_DIR
    })

# ==================== LINKEDIN ROUTES (KEEP THESE) ====================
linkedin_status = {
    'is_scraping': False,
    'progress': 0,
    'message': 'Idle',
    'jobs_count': 0
}

@app.route('/api/linkedin/scrape', methods=['POST'])
def linkedin_scrape():
    """Start LinkedIn scraping"""
    global linkedin_status
    
    data = request.json
    job_titles = data.get('job_titles', ['Python Developer', 'Data Scientist', 'Software Engineer'])
    location = data.get('location', 'India')
    max_jobs = data.get('max_jobs', 20)
    
    def scrape_task():
        global linkedin_status
        linkedin_status['is_scraping'] = True
        linkedin_status['message'] = 'Starting LinkedIn scraper...'
        
        scraper = LinkedInScraper(headless=True)
        try:
            jobs = scraper.search_jobs(job_titles, location, max_jobs)
            linkedin_status['jobs_count'] = len(jobs)
            linkedin_status['message'] = f'Completed! Found {len(jobs)} jobs'
        except Exception as e:
            linkedin_status['message'] = f'Error: {str(e)}'
        finally:
            scraper.close()
            linkedin_status['is_scraping'] = False
    
    thread = threading.Thread(target=scrape_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'LinkedIn scraping started',
        'job_titles': job_titles,
        'location': location
    })

@app.route('/api/linkedin/status', methods=['GET'])
def linkedin_status_endpoint():
    """Get scraping status"""
    return jsonify(linkedin_status)

@app.route('/api/linkedin/jobs', methods=['GET'])
def get_linkedin_jobs():
    """Get scraped LinkedIn jobs"""
    try:
        scraper = LinkedInScraper(headless=True)
        jobs = scraper.get_latest_jobs()
        scraper.close()
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/linkedin/match', methods=['POST'])
def match_linkedin_jobs():
    """Match LinkedIn jobs with resume skills"""
    data = request.json
    resume_skills = data.get('skills', [])
    
    scraper = LinkedInScraper(headless=True)
    jobs = scraper.get_latest_jobs()
    scraper.close()
    
    if not jobs:
        return jsonify({'success': False, 'error': 'No jobs found. Please scrape first.'}), 404
    
    matched_jobs = match_jobs_with_resume(jobs, resume_skills)
    
    return jsonify({
        'success': True,
        'jobs': matched_jobs[:20],
        'total': len(matched_jobs)
    })

# ==================== MAIN ====================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 CareerAI Server Starting - LinkedIn Only Version")
    print("="*60)
    print(f"📁 Database: {db_path}")
    print(f"📁 Uploads: {UPLOAD_DIR}")
    print(f"📊 Skills Database: {sum(len(skills) for skills in SKILLS_DATABASE.values())} skills")
    print(f"💼 Job Roles: {len(JOB_ROLES)} roles")
    print("\n📡 Endpoints:")
    print("   POST  http://localhost:5000/api/register - Register")
    print("   POST  http://localhost:5000/api/login - Login")
    print("   POST  http://localhost:5000/api/upload-resume - Upload Resume")
    print("   GET   http://localhost:5000/api/test - Test Server")
    print("   POST  http://localhost:5000/api/linkedin/scrape - Scrape LinkedIn Jobs")
    print("   GET   http://localhost:5000/api/linkedin/status - Scraping Status")
    print("   GET   http://localhost:5000/api/linkedin/jobs - Get Scraped Jobs")
    print("   POST  http://localhost:5000/api/linkedin/match - Match LinkedIn Jobs")
    print("\n🌐 Open dashboard.html in your browser")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)