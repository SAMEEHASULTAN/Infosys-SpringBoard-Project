// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Store user data
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;

// Chart instances
let scoreGauge = null;
let skillsPieChart = null;
let skillsBarChart = null;
let salaryChart = null;

// Debug mode
const DEBUG = true;

function debugLog(...args) {
    if (DEBUG) console.log("[DEBUG]", ...args);
}

// Test server connection
async function testServerConnection() {
    try {
        const response = await fetch(`http://localhost:5000/api/test`);
        const data = await response.json();
        return true;
    } catch (error) {
        showNotification('⚠️ Backend server not running. Start with: python app.py', 'error');
        return false;
    }
}

// Initialize charts
function initCharts() {
    // Score Gauge
    const gaugeCtx = document.getElementById('scoreGauge')?.getContext('2d');
    if (gaugeCtx) {
        scoreGauge = new Chart(gaugeCtx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#667eea', '#f0f0f0'],
                    borderWidth: 0,
                    circumference: 270,
                    rotation: 225
                }]
            },
            options: { cutout: '70%', responsive: true, plugins: { legend: { display: false } } }
        });
    }
    
    // Skills Pie Chart
    const pieCtx = document.getElementById('skillsPieChart')?.getContext('2d');
    if (pieCtx) {
        skillsPieChart = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['Technical', 'Soft Skills', 'Tools'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#667eea', '#4facfe', '#84fab0']
                }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    }
    
    // Skills Bar Chart
    const barCtx = document.getElementById('skillsBarChart')?.getContext('2d');
    if (barCtx) {
        skillsBarChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: ['Python', 'JavaScript', 'SQL', 'React', 'AWS'],
                datasets: [{
                    label: 'Your Skills',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: '#667eea'
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
        });
    }
    
    // Salary Chart
    const salaryCtx = document.getElementById('salaryChart')?.getContext('2d');
    if (salaryCtx) {
        salaryChart = new Chart(salaryCtx, {
            type: 'line',
            data: {
                labels: ['Entry', 'Junior', 'Mid', 'Senior', 'Lead'],
                datasets: [{
                    label: 'Salary (LPA)',
                    data: [4, 8, 15, 25, 35],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102,126,234,0.1)',
                    tension: 0.4,
                    fill: true
                }]
            }
        });
    }
}

// Document Ready
document.addEventListener('DOMContentLoaded', async () => {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    
    if (registerForm) registerForm.addEventListener('submit', handleRegister);
    if (loginForm) loginForm.addEventListener('submit', handleLogin);
    
    const filename = window.location.pathname.split('/').pop();
    
    if (filename === 'dashboard.html') {
        await testServerConnection();
        
        if (!currentUser) {
            window.location.href = 'login.html';
            return;
        }
        
        document.getElementById('userName').textContent = `${currentUser.first_name || ''} ${currentUser.last_name || ''}`;
        document.getElementById('welcomeName').textContent = currentUser.first_name || 'User';
        
        initCharts();
        setupResumeUpload();
        
        const savedData = localStorage.getItem('analysisData');
        if (savedData) displayEnhancedResults(JSON.parse(savedData));
    }
});

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `<i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i> ${message}`;
    
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px; padding: 15px 25px;
        border-radius: 10px; color: white; font-weight: 500; z-index: 9999;
        background: ${type === 'error' ? 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' : 
                     type === 'success' ? 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)' : 
                     'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => document.body.removeChild(notification), 4000);
}

// Handle Registration
async function handleRegister(e) {
    e.preventDefault();
    
    const userData = {
        firstName: document.getElementById('firstName')?.value,
        lastName: document.getElementById('lastName')?.value,
        email: document.getElementById('email')?.value,
        mobile: document.getElementById('mobile')?.value,
        password: document.getElementById('password')?.value
    };
    
    const confirmPassword = document.getElementById('confirmPassword')?.value;
    
    if (!userData.firstName || !userData.lastName || !userData.email || !userData.mobile || !userData.password) {
        showNotification('Please fill all fields', 'error'); return;
    }
    if (userData.password !== confirmPassword) {
        showNotification('Passwords do not match!', 'error'); return;
    }
    if (userData.mobile.length !== 10 || isNaN(userData.mobile)) {
        showNotification('Enter valid 10-digit mobile number', 'error'); return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        const data = await response.json();
        if (response.ok) {
            showNotification('🎉 Registration successful! Please login.', 'success');
            setTimeout(() => window.location.href = 'login.html', 1500);
        } else showNotification(data.error || 'Registration failed', 'error');
    } catch (error) {
        showNotification('Server connection failed', 'error');
    }
}

// Handle Login
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email')?.value;
    const password = document.getElementById('password')?.value;
    
    if (!email || !password) {
        showNotification('Please enter email and password', 'error'); return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (response.ok) {
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showNotification('✅ Login successful!', 'success');
            setTimeout(() => window.location.href = 'dashboard.html', 1000);
        } else showNotification('Invalid email or password', 'error');
    } catch (error) {
        showNotification('Server connection failed', 'error');
    }
}

// Logout
function logout() {
    localStorage.removeItem('currentUser');
    localStorage.removeItem('analysisData');
    showNotification('👋 Logged out successfully', 'info');
    setTimeout(() => window.location.href = 'index.html', 1000);
}

// Setup Resume Upload
function setupResumeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const resumeFile = document.getElementById('resumeFile');
    
    if (!uploadArea || !resumeFile) return;
    
    uploadArea.addEventListener('click', () => resumeFile.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = 'rgba(102,126,234,0.1)';
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f8f9ff';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f8f9ff';
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') uploadResume(file);
        else showNotification('Please upload a PDF file', 'error');
    });
    
    resumeFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file && file.type === 'application/pdf') uploadResume(file);
        else showNotification('Please upload a PDF file', 'error');
    });
}

// Upload Resume
async function uploadResume(file) {
    document.getElementById('uploadProgress')?.classList.remove('d-none');
    document.getElementById('loadingSpinner').style.display = 'block';
    
    const formData = new FormData();
    formData.append('resume', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload-resume`, {
            method: 'POST', body: formData
        });
        const data = await response.json();
        
        document.getElementById('uploadProgress')?.classList.add('d-none');
        document.getElementById('loadingSpinner').style.display = 'none';
        
        if (response.ok && data.success) {
            localStorage.setItem('analysisData', JSON.stringify(data));
            displayEnhancedResults(data);
            document.getElementById('overview-tab')?.click();
            showNotification('✨ Resume analyzed successfully!', 'success');
        } else showNotification('Error: ' + (data.error || 'Processing failed'), 'error');
    } catch (error) {
        document.getElementById('uploadProgress')?.classList.add('d-none');
        document.getElementById('loadingSpinner').style.display = 'none';
        showNotification('Network error', 'error');
    }
}

// Display Results
function displayEnhancedResults(data) {
    updateScoreDisplay(data);
    updateSkillsDistribution(data);
    updateProfileStrength(data);
    updateTopSkills(data);
    updateCategorizedSkills(data);
    updateSkillGaps(data);
    updateCharts(data);
}

// Update Score Display
function updateScoreDisplay(data) {
    const score = data.score || 0;
    document.getElementById('resumeScore').textContent = score;
    
    if (scoreGauge) {
        scoreGauge.data.datasets[0].data = [score, 100 - score];
        scoreGauge.update();
    }
    
    let grade = score >= 80 ? 'A - Excellent' : score >= 60 ? 'B - Good' : 
                score >= 40 ? 'C - Average' : 'D - Needs Work';
    document.getElementById('scoreGrade').textContent = grade;
    document.getElementById('scoreDetails').textContent = 
        `${data.skills_found?.length || 0} skills, ${data.matched_roles?.length || 0} matching roles`;
}

// Update Skills Distribution
function updateSkillsDistribution(data) {
    const categorized = data.categorized_skills || {};
    let techCount = 0, softCount = 0, toolsCount = 0;
    
    if (categorized.programming_languages) techCount += categorized.programming_languages.length;
    if (categorized.frontend) techCount += categorized.frontend.length;
    if (categorized.backend) techCount += categorized.backend.length;
    if (categorized.data_science) techCount += categorized.data_science.length;
    if (categorized.soft_skills) softCount = categorized.soft_skills.length;
    if (categorized.tools) toolsCount += categorized.tools.length;
    if (categorized.devops) toolsCount += categorized.devops.length;
    if (categorized.database) toolsCount += categorized.database.length;
    
    document.getElementById('techCount').textContent = techCount;
    document.getElementById('softCount').textContent = softCount;
    document.getElementById('toolsCount').textContent = toolsCount;
    
    if (skillsPieChart) {
        skillsPieChart.data.datasets[0].data = [techCount, softCount, toolsCount];
        skillsPieChart.update();
    }
}

// Update Profile Strength
function updateProfileStrength(data) {
    const score = data.score || 0;
    document.getElementById('skillsCoverage').textContent = `${score}%`;
    document.getElementById('skillsCoverageBar').style.width = `${score}%`;
    
    const jobMatch = Math.min(score + 10, 100);
    document.getElementById('jobMatch').textContent = `${jobMatch}%`;
    document.getElementById('jobMatchBar').style.width = `${jobMatch}%`;
    
    document.getElementById('skillGap').textContent = `${100 - score}%`;
    document.getElementById('skillGapBar').style.width = `${100 - score}%`;
    
    const expYears = data.experience_years || 0;
    let expLevel = 'Entry Level', expWidth = 25;
    if (expYears >= 5) { expLevel = 'Senior Level'; expWidth = 90; }
    else if (expYears >= 3) { expLevel = 'Mid Level'; expWidth = 60; }
    else if (expYears >= 1) { expLevel = 'Junior Level'; expWidth = 35; }
    
    document.getElementById('expLevel').textContent = `${expLevel} (${expYears} years)`;
    document.getElementById('expBar').style.width = `${expWidth}%`;
}

// Update Top Skills
function updateTopSkills(data) {
    const skills = data.skills_found || [];
    const container = document.getElementById('topSkills');
    container.innerHTML = '';
    
    if (skills.length > 0) {
        skills.slice(0, 10).forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'skill-badge technical';
            badge.textContent = skill.charAt(0).toUpperCase() + skill.slice(1);
            container.appendChild(badge);
        });
    } else container.innerHTML = '<p class="text-muted">No skills found</p>';
}

// Update Categorized Skills
function updateCategorizedSkills(data) {
    const categorized = data.categorized_skills || {};
    
    const techSkills = [
        ...(categorized.programming_languages || []),
        ...(categorized.frontend || []),
        ...(categorized.backend || []),
        ...(categorized.data_science || [])
    ];
    
    const techDiv = document.getElementById('technicalSkills');
    techDiv.innerHTML = '';
    if (techSkills.length > 0) {
        techSkills.forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'skill-badge technical';
            badge.textContent = skill.charAt(0).toUpperCase() + skill.slice(1);
            techDiv.appendChild(badge);
        });
    } else techDiv.innerHTML = '<p class="text-muted">No technical skills detected</p>';
    
    const softSkills = categorized.soft_skills || [];
    const softDiv = document.getElementById('softSkills');
    softDiv.innerHTML = '';
    if (softSkills.length > 0) {
        softSkills.forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'skill-badge soft';
            badge.textContent = skill.charAt(0).toUpperCase() + skill.slice(1);
            softDiv.appendChild(badge);
        });
    } else softDiv.innerHTML = '<p class="text-muted">No soft skills detected</p>';
    
    const toolSkills = [
        ...(categorized.tools || []),
        ...(categorized.devops || []),
        ...(categorized.database || [])
    ];
    
    const toolDiv = document.getElementById('toolSkills');
    toolDiv.innerHTML = '';
    if (toolSkills.length > 0) {
        toolSkills.forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'skill-badge tool';
            badge.textContent = skill.charAt(0).toUpperCase() + skill.slice(1);
            toolDiv.appendChild(badge);
        });
    } else toolDiv.innerHTML = '<p class="text-muted">No tools detected</p>';
}

// Update Skill Gaps
function updateSkillGaps(data) {
    const gaps = data.skill_gaps || {};
    const container = document.getElementById('skillGapsContainer');
    container.innerHTML = '';
    
    if (Object.keys(gaps).length > 0) {
        for (const [role, skills] of Object.entries(gaps)) {
            container.innerHTML += `
                <div class="gap-item">
                    <div class="gap-role"><i class="fas fa-briefcase"></i> ${role}</div>
                    <div>${skills.map(s => `<span class="gap-skill"><i class="fas fa-plus-circle"></i> ${s}</span>`).join('')}</div>
                </div>
            `;
        }
    } else container.innerHTML = '<div class="gap-item"><p class="text-success">🎉 No skill gaps found!</p></div>';
}

// Update Charts
function updateCharts(data) {
    if (skillsBarChart && data.matched_roles && data.matched_roles.length > 0) {
        const topRoles = data.matched_roles.slice(0, 5);
        skillsBarChart.data.labels = topRoles.map(r => r.title);
        skillsBarChart.data.datasets[0].data = topRoles.map(r => r.match_percentage);
        skillsBarChart.update();
    }
}

// Show detailed score
function showDetailedScore() {
    const data = JSON.parse(localStorage.getItem('analysisData'));
    if (!data) { showNotification('Upload resume first', 'error'); return; }
    showNotification(`📊 Score: ${data.score}% | Skills: ${data.skills_found?.length || 0} | Experience: ${data.experience_years || 0} years`, 'info');
}

// Show learning resources
function showLearningResources() {
    window.open('https://www.coursera.org', '_blank');
}

// ==================== LINKEDIN FUNCTIONS (KEEP ALL) ====================

// Scrape LinkedIn Jobs
async function scrapeLinkedInJobs() {
    const btn = document.getElementById('scrapeBtn');
    const statusDiv = document.getElementById('scrapingStatus');
    const statusMsg = document.getElementById('statusMessage');
    
    if (!btn || !statusDiv || !statusMsg) return;
    
    statusDiv.classList.remove('d-none');
    statusMsg.innerHTML = '🕷️ Starting LinkedIn scraper...';
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/linkedin/scrape`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_titles: ['Python Developer', 'Data Scientist', 'Software Engineer'],
                location: 'India',
                max_jobs: 20
            })
        });
        
        if (response.ok) {
            statusMsg.innerHTML = '✅ Scraping started! This will take 2-3 minutes.';
            setTimeout(checkScrapingStatus, 5000);
            setTimeout(checkScrapingStatus, 15000);
            setTimeout(checkScrapingStatus, 30000);
            setTimeout(checkScrapingStatus, 60000);
            setTimeout(checkScrapingStatus, 120000);
            setTimeout(checkScrapingStatus, 180000);
        } else statusMsg.innerHTML = '❌ Error starting scraper';
    } catch (error) {
        statusMsg.innerHTML = `❌ Connection error`;
    }
    
    setTimeout(() => {
        btn.innerHTML = '<i class="fab fa-linkedin"></i> Scrape LinkedIn Jobs';
        btn.disabled = false;
    }, 5000);
}

// Check Scraping Status
async function checkScrapingStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/linkedin/status`);
        const status = await response.json();
        const statusMsg = document.getElementById('statusMessage');
        
        if (statusMsg) {
            statusMsg.innerHTML = `📊 Status: ${status.message} (${status.jobs_count} jobs found)`;
            
            if (!status.is_scraping && status.jobs_count > 0) {
                statusMsg.innerHTML = `✅ Complete! Found ${status.jobs_count} jobs. Loading...`;
                setTimeout(() => loadLinkedInJobs(), 2000);
            }
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Load LinkedIn Jobs
async function loadLinkedInJobs() {
    const container = document.getElementById('jobRecommendations');
    if (!container) return;
    
    container.innerHTML = `<div class="text-center py-5"><div class="spinner-border"></div><p>Loading LinkedIn jobs...</p></div>`;
    document.getElementById('jobs-tab')?.click();
    
    try {
        const analysisData = JSON.parse(localStorage.getItem('analysisData') || '{}');
        const userSkills = analysisData.skills_found || [];
        
        const response = await fetch(`${API_BASE_URL}/linkedin/jobs`);
        const data = await response.json();
        
        if (data.success && data.jobs.length > 0) {
            const matchResponse = await fetch(`${API_BASE_URL}/linkedin/match`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ skills: userSkills })
            });
            const matchData = await matchResponse.json();
            displayLinkedInJobs(matchData.jobs || data.jobs);
            showNotification(`✅ Found ${data.jobs.length} LinkedIn jobs!`, 'success');
            document.getElementById('scrapingStatus')?.classList.add('d-none');
        } else {
            container.innerHTML = '<div class="text-center py-5"><p>No LinkedIn jobs found. Scrape first.</p></div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="text-center py-5 text-danger">Error loading jobs</div>';
    }
}

// Display LinkedIn Jobs
function displayLinkedInJobs(jobs) {
    const container = document.getElementById('jobRecommendations');
    if (!jobs || jobs.length === 0) {
        container.innerHTML = '<div class="text-center py-5"><p>No LinkedIn jobs found</p></div>';
        return;
    }
    
    let html = '<div class="row"><div class="col-12 mb-3"><h5><i class="fab fa-linkedin text-primary"></i> LinkedIn Jobs</h5></div>';
    
    jobs.slice(0, 12).forEach(job => {
        const matchPercent = job.match_percentage || 75;
        let matchClass = matchPercent >= 80 ? 'match-high' : matchPercent >= 70 ? 'match-medium' : 'match-low';
        const linkedinColor = '#0A66C2';
        
        html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="job-card">
                    <span class="match-badge ${matchClass}">${matchPercent}% Match</span>
                    <h5 class="mt-3">${job.title || 'Software Developer'}</h5>
                    <p class="text-primary mb-2"><i class="fas fa-building"></i> ${job.company || 'Unknown'}</p>
                    <p class="mb-2">
                        <i class="fas fa-map-marker-alt text-muted"></i> ${job.location || 'India'}<br>
                        <i class="fas fa-clock text-muted"></i> ${job.posted_date || 'Recently'}<br>
                        <i class="fab fa-linkedin text-muted"></i> LinkedIn
                    </p>
                    <div class="mb-3">${(job.skills || []).slice(0, 5).map(s => `<span class="badge bg-light text-dark me-1">${s}</span>`).join('')}</div>
                    <button class="quick-action-btn w-100" onclick="window.open('${job.url || '#'}', '_blank')" style="background: ${linkedinColor}; color: white; border: none;">
                        <i class="fab fa-linkedin"></i> Apply on LinkedIn
                    </button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Force load LinkedIn jobs (for debugging)
async function forceLoadLinkedInJobs() {
    await loadLinkedInJobs();
}