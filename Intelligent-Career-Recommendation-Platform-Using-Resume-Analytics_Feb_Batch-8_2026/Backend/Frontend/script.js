// API Base URL - Points to your backend
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
    if (DEBUG) {
        console.log("[DEBUG]", ...args);
    }
}

// Test server connection first
async function testServerConnection() {
    try {
        debugLog("Testing server connection...");
        const response = await fetch(`http://localhost:5000/api/test`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        debugLog("Server connected:", data);
        return true;
    } catch (error) {
        console.error("❌ Server connection failed:", error);
        showNotification('⚠️ Backend server is not running. Please start the server with: python app.py', 'error');
        return false;
    }
}

// Initialize all charts
function initCharts() {
    debugLog("Initializing charts...");
    
    // Score Gauge Chart
    const gaugeCtx = document.getElementById('scoreGauge')?.getContext('2d');
    if (gaugeCtx) {
        if (scoreGauge) scoreGauge.destroy();
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
            options: {
                cutout: '70%',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }
    
    // Skills Pie Chart
    const pieCtx = document.getElementById('skillsPieChart')?.getContext('2d');
    if (pieCtx) {
        if (skillsPieChart) skillsPieChart.destroy();
        skillsPieChart = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['Technical', 'Soft Skills', 'Tools'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#667eea', '#4facfe', '#84fab0'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
    
    // Skills Bar Chart
    const barCtx = document.getElementById('skillsBarChart')?.getContext('2d');
    if (barCtx) {
        if (skillsBarChart) skillsBarChart.destroy();
        skillsBarChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: ['Python', 'JavaScript', 'SQL', 'React', 'AWS'],
                datasets: [{
                    label: 'Your Proficiency',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: '#667eea'
                },
                {
                    label: 'Market Demand',
                    data: [95, 90, 85, 88, 92],
                    backgroundColor: '#ffc107'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
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
            },
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });
    }
}

// Document Ready
document.addEventListener('DOMContentLoaded', async () => {
    debugLog("DOM loaded");
    
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Check which page we're on
    const path = window.location.pathname;
    const filename = path.split('/').pop();
    debugLog("Current page:", filename);
    
    // Dashboard page
    if (filename === 'dashboard.html') {
        debugLog("Dashboard page detected");
        
        // Test server connection first
        const isConnected = await testServerConnection();
        
        if (!currentUser) {
            debugLog("No user logged in");
            window.location.href = 'login.html';
            return;
        }
        
        // Update user info
        const userNameSpan = document.getElementById('userName');
        const welcomeNameSpan = document.getElementById('welcomeName');
        
        if (userNameSpan) {
            userNameSpan.textContent = `${currentUser.first_name || ''} ${currentUser.last_name || ''}`;
        }
        if (welcomeNameSpan) {
            welcomeNameSpan.textContent = currentUser.first_name || 'User';
        }
        
        // Initialize charts
        initCharts();
        
        // Setup resume upload
        setupResumeUpload();
        
        // Check for saved analysis
        const savedData = localStorage.getItem('analysisData');
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                debugLog("Found saved analysis data");
                displayEnhancedResults(data);
            } catch (e) {
                debugLog("No valid saved data");
            }
        }
        
        if (!isConnected) {
            showNotification('⚠️ Backend server not running. Please start the server with: python app.py', 'error');
        } else {
            showNotification('✅ Connected to server! Ready to upload resume.', 'success');
        }
    }
    
    // Login page
    if (filename === 'login.html') {
        debugLog("Login page detected");
    }
    
    // Register page
    if (filename === 'register.html') {
        debugLog("Register page detected");
    }
    
    // Index page
    if (filename === 'index.html' || filename === '') {
        debugLog("Index page detected");
    }
});

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        ${message}
    `;
    
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '15px 25px';
    notification.style.borderRadius = '10px';
    notification.style.color = 'white';
    notification.style.fontWeight = '500';
    notification.style.zIndex = '9999';
    notification.style.animation = 'slideIn 0.3s ease';
    notification.style.boxShadow = '0 5px 20px rgba(0,0,0,0.2)';
    
    if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
    } else if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 4000);
}

// Handle Registration
async function handleRegister(e) {
    e.preventDefault();
    
    const firstName = document.getElementById('firstName')?.value;
    const lastName = document.getElementById('lastName')?.value;
    const email = document.getElementById('email')?.value;
    const mobile = document.getElementById('mobile')?.value;
    const password = document.getElementById('password')?.value;
    const confirmPassword = document.getElementById('confirmPassword')?.value;
    
    if (!firstName || !lastName || !email || !mobile || !password) {
        showNotification('Please fill all fields', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showNotification('Passwords do not match!', 'error');
        return;
    }
    
    if (mobile.length !== 10 || isNaN(mobile)) {
        showNotification('Enter valid 10-digit mobile number', 'error');
        return;
    }
    
    const userData = { firstName, lastName, email, mobile, password };
    debugLog("Registering user:", { ...userData, password: '***' });
    
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        debugLog("Registration response:", data);
        
        if (response.ok) {
            showNotification('🎉 Registration successful! Please login.', 'success');
            setTimeout(() => window.location.href = 'login.html', 1500);
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showNotification('Server connection failed. Is the backend running?', 'error');
    }
}

// Handle Login
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email')?.value;
    const password = document.getElementById('password')?.value;
    
    if (!email || !password) {
        showNotification('Please enter email and password', 'error');
        return;
    }
    
    debugLog("Logging in user:", { email, password: '***' });
    
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        debugLog("Login response:", data);
        
        if (response.ok) {
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showNotification('✅ Login successful!', 'success');
            setTimeout(() => window.location.href = 'dashboard.html', 1000);
        } else {
            showNotification('Invalid email or password', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Server connection failed. Is the backend running?', 'error');
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
    
    if (!uploadArea || !resumeFile) {
        debugLog("Upload elements not found");
        return;
    }
    
    uploadArea.addEventListener('click', () => resumeFile.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = 'rgba(102,126,234,0.1)';
        uploadArea.style.borderColor = '#764ba2';
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f8f9ff';
        uploadArea.style.borderColor = '#667eea';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f8f9ff';
        uploadArea.style.borderColor = '#667eea';
        
        const file = e.dataTransfer.files[0];
        if (file) {
            debugLog("File dropped:", file.name, "Type:", file.type);
            if (file.type === 'application/pdf') {
                uploadResume(file);
            } else {
                showNotification('Please upload a PDF file', 'error');
            }
        }
    });
    
    resumeFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            debugLog("File selected:", file.name, "Type:", file.type);
            if (file.type === 'application/pdf') {
                uploadResume(file);
            } else {
                showNotification('Please upload a PDF file', 'error');
            }
        }
    });
    
    debugLog("Resume upload setup complete");
}

// Upload Resume
async function uploadResume(file) {
    debugLog("Starting resume upload:", file.name);
    
    const uploadProgress = document.getElementById('uploadProgress');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    if (uploadProgress) uploadProgress.classList.remove('d-none');
    if (loadingSpinner) loadingSpinner.style.display = 'block';
    
    const formData = new FormData();
    formData.append('resume', file);
    
    try {
        debugLog("Sending to server...");
        
        const response = await fetch(`${API_BASE_URL}/upload-resume`, {
            method: 'POST',
            body: formData
        });
        
        debugLog("Response status:", response.status);
        
        const data = await response.json();
        debugLog("Server response:", data);
        
        if (uploadProgress) uploadProgress.classList.add('d-none');
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        
        if (response.ok && data.success) {
            debugLog("Resume processed successfully");
            
            // Store the data
            localStorage.setItem('analysisData', JSON.stringify(data));
            
            // Display results
            displayEnhancedResults(data);
            
            // Switch to overview tab
            const overviewTab = document.getElementById('overview-tab');
            if (overviewTab) {
                overviewTab.click();
            }
            
            showNotification('✨ Resume analyzed successfully!', 'success');
        } else {
            console.error("Server error:", data);
            showNotification('Error: ' + (data.error || 'Processing failed'), 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        if (uploadProgress) uploadProgress.classList.add('d-none');
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        showNotification('Network error: Could not connect to server. Is the backend running?', 'error');
    }
}

// Display Enhanced Results
function displayEnhancedResults(data) {
    debugLog("Displaying results:", data);
    
    // Check if data exists
    if (!data) {
        console.error("No data to display");
        return;
    }
    
    // Update score
    updateScoreDisplay(data);
    
    // Update skills distribution
    updateSkillsDistribution(data);
    
    // Update profile strength
    updateProfileStrength(data);
    
    // Update top skills
    updateTopSkills(data);
    
    // Update categorized skills
    updateCategorizedSkills(data);
    
    // Update skill gaps
    updateSkillGaps(data);
    
    // Update charts
    updateCharts(data);
}

// Update Score Display
function updateScoreDisplay(data) {
    const score = data.score || 0;
    const scoreElement = document.getElementById('resumeScore');
    const gradeElement = document.getElementById('scoreGrade');
    const detailsElement = document.getElementById('scoreDetails');
    
    if (scoreElement) {
        scoreElement.textContent = score;
    }
    
    // Update gauge chart
    if (scoreGauge) {
        scoreGauge.data.datasets[0].data = [score, 100 - score];
        scoreGauge.update();
    }
    
    // Set grade
    let grade, color;
    if (score >= 80) { 
        grade = 'A - Excellent'; 
        color = '#84fab0';
    } else if (score >= 60) { 
        grade = 'B - Good'; 
        color = '#4facfe';
    } else if (score >= 40) { 
        grade = 'C - Average'; 
        color = '#f6d365';
    } else { 
        grade = 'D - Needs Work'; 
        color = '#f093fb';
    }
    
    if (gradeElement) {
        gradeElement.textContent = grade;
        gradeElement.style.color = color;
    }
    
    if (detailsElement) {
        const totalSkills = data.skills_found?.length || 0;
        const totalRoles = data.matched_roles?.length || 0;
        detailsElement.textContent = `${totalSkills} skills, ${totalRoles} matching roles`;
    }
}

// Update Skills Distribution
function updateSkillsDistribution(data) {
    // Categorize skills
    const categorized = data.categorized_skills || {};
    
    let techCount = 0;
    let softCount = 0;
    let toolsCount = 0;
    
    // Count technical skills
    if (categorized.programming_languages) techCount += categorized.programming_languages.length;
    if (categorized.frontend) techCount += categorized.frontend.length;
    if (categorized.backend) techCount += categorized.backend.length;
    if (categorized.data_science) techCount += categorized.data_science.length;
    
    // Count soft skills
    if (categorized.soft_skills) softCount = categorized.soft_skills.length;
    
    // Count tools
    if (categorized.tools) toolsCount += categorized.tools.length;
    if (categorized.devops) toolsCount += categorized.devops.length;
    if (categorized.database) toolsCount += categorized.database.length;
    
    debugLog("Skills counts - Tech:", techCount, "Soft:", softCount, "Tools:", toolsCount);
    
    // Update counts
    const techCountEl = document.getElementById('techCount');
    const softCountEl = document.getElementById('softCount');
    const toolsCountEl = document.getElementById('toolsCount');
    
    if (techCountEl) techCountEl.textContent = techCount;
    if (softCountEl) softCountEl.textContent = softCount;
    if (toolsCountEl) toolsCountEl.textContent = toolsCount;
    
    // Update pie chart
    if (skillsPieChart) {
        skillsPieChart.data.datasets[0].data = [techCount, softCount, toolsCount];
        skillsPieChart.update();
    }
}

// Update Profile Strength
function updateProfileStrength(data) {
    const score = data.score || 0;
    
    // Skills Coverage
    const skillsCoverage = document.getElementById('skillsCoverage');
    const skillsCoverageBar = document.getElementById('skillsCoverageBar');
    if (skillsCoverage) skillsCoverage.textContent = `${score}%`;
    if (skillsCoverageBar) skillsCoverageBar.style.width = `${score}%`;
    
    // Job Market Match
    const jobMatch = Math.min(score + 10, 100);
    const jobMatchEl = document.getElementById('jobMatch');
    const jobMatchBar = document.getElementById('jobMatchBar');
    if (jobMatchEl) jobMatchEl.textContent = `${jobMatch}%`;
    if (jobMatchBar) jobMatchBar.style.width = `${jobMatch}%`;
    
    // Skill Gap
    const skillGap = 100 - score;
    const skillGapEl = document.getElementById('skillGap');
    const skillGapBar = document.getElementById('skillGapBar');
    if (skillGapEl) skillGapEl.textContent = `${skillGap}%`;
    if (skillGapBar) skillGapBar.style.width = `${skillGap}%`;
    
    // Experience Level
    const expYears = data.experience_years || 0;
    let expLevel = 'Entry Level';
    let expWidth = 25;
    
    if (expYears >= 5) { 
        expLevel = 'Senior Level'; 
        expWidth = 90;
    } else if (expYears >= 3) { 
        expLevel = 'Mid Level'; 
        expWidth = 60;
    } else if (expYears >= 1) { 
        expLevel = 'Junior Level'; 
        expWidth = 35;
    }
    
    const expLevelEl = document.getElementById('expLevel');
    const expBar = document.getElementById('expBar');
    
    if (expLevelEl) expLevelEl.textContent = `${expLevel} (${expYears} years)`;
    if (expBar) {
        expBar.style.width = `${expWidth}%`;
        expBar.textContent = `${expWidth}%`;
    }
}

// Update Top Skills
function updateTopSkills(data) {
    const skillsFound = data.skills_found || [];
    const topSkills = document.getElementById('topSkills');
    
    if (!topSkills) return;
    
    topSkills.innerHTML = '';
    
    if (skillsFound.length > 0) {
        skillsFound.slice(0, 10).forEach(skill => {
            const badge = document.createElement('span');
            badge.className = 'skill-badge technical';
            badge.textContent = skill.charAt(0).toUpperCase() + skill.slice(1);
            topSkills.appendChild(badge);
        });
    } else {
        topSkills.innerHTML = '<p class="text-muted">No skills found in resume</p>';
    }
}

// Update Categorized Skills
function updateCategorizedSkills(data) {
    const categorized = data.categorized_skills || {};
    
    // Technical Skills
    const techSkills = [
        ...(categorized.programming_languages || []),
        ...(categorized.frontend || []),
        ...(categorized.backend || []),
        ...(categorized.data_science || [])
    ];
    
    const techDiv = document.getElementById('technicalSkills');
    if (techDiv) {
        techDiv.innerHTML = '';
        if (techSkills.length > 0) {
            techSkills.forEach(skill => {
                const badge = document.createElement('span');
                badge.className = 'skill-badge technical';
                badge.textContent = skill.charAt(0).toUpperCase() + skill.slice(1);
                techDiv.appendChild(badge);
            });
        } else {
            techDiv.innerHTML = '<p class="text-muted">No technical skills detected</p>';
        }
    }
    
    // Soft Skills
    const softSkills = categorized.soft_skills || [];
    const softDiv = document.getElementById('softSkills');
    if (softDiv) {
        softDiv.innerHTML = '';
        if (softSkills.length > 0) {
            softSkills.forEach(skill => {
                const badge = document.createElement('span');
                badge.className = 'skill-badge soft';
                badge.textContent = skill.charAt(0).toUpperCase() + skill.slice(1);
                softDiv.appendChild(badge);
            });
        } else {
            softDiv.innerHTML = '<p class="text-muted">No soft skills detected</p>';
        }
    }
    
    // Tools
    const toolSkills = [
        ...(categorized.tools || []),
        ...(categorized.devops || []),
        ...(categorized.database || [])
    ];
    
    const toolDiv = document.getElementById('toolSkills');
    if (toolDiv) {
        toolDiv.innerHTML = '';
        if (toolSkills.length > 0) {
            toolSkills.forEach(skill => {
                const badge = document.createElement('span');
                badge.className = 'skill-badge tool';
                badge.textContent = skill.charAt(0).toUpperCase() + skill.slice(1);
                toolDiv.appendChild(badge);
            });
        } else {
            toolDiv.innerHTML = '<p class="text-muted">No tools detected</p>';
        }
    }
}

// Update Skill Gaps
function updateSkillGaps(data) {
    const gaps = data.skill_gaps || {};
    const container = document.getElementById('skillGapsContainer');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    if (Object.keys(gaps).length > 0) {
        for (const [role, skills] of Object.entries(gaps)) {
            const gapDiv = document.createElement('div');
            gapDiv.className = 'gap-item';
            gapDiv.innerHTML = `
                <div class="gap-role">
                    <i class="fas fa-briefcase"></i> ${role}
                </div>
                <div>
                    ${skills.map(s => `<span class="gap-skill"><i class="fas fa-plus-circle"></i> ${s}</span>`).join('')}
                </div>
                <div class="mt-2">
                    <small class="text-muted">Learn these skills to improve your match</small>
                </div>
            `;
            container.appendChild(gapDiv);
        }
    } else {
        container.innerHTML = '<div class="gap-item"><p class="text-success">🎉 No skill gaps found! Great job!</p></div>';
    }
}

// Update Charts
function updateCharts(data) {
    // Update bar chart with matched roles
    if (skillsBarChart && data.matched_roles && data.matched_roles.length > 0) {
        const topRoles = data.matched_roles.slice(0, 5);
        skillsBarChart.data.labels = topRoles.map(r => r.title);
        skillsBarChart.data.datasets[0].data = topRoles.map(r => r.match_percentage);
        skillsBarChart.update();
    }
}

// View Job Recommendations
async function viewJobRecommendations() {
    const data = JSON.parse(localStorage.getItem('analysisData'));
    if (!data) {
        showNotification('Please upload your resume first', 'error');
        return;
    }
    
    const btn = document.getElementById('viewJobsBtn');
    if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Finding jobs from JSearch...';
        btn.disabled = true;
    }
    
    // Show loading in jobs tab
    const container = document.getElementById('jobRecommendations');
    container.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>Searching for jobs matching your skills...</p>
        </div>
    `;
    
    // Switch to jobs tab
    const jobsTab = document.getElementById('jobs-tab');
    if (jobsTab) {
        jobsTab.click();
    }
    
    try {
        // Call backend to get jobs with JSearch
        const skills = data.skills_found?.join(',') || '';
        const response = await fetch(`${API_BASE_URL}/jobs/search?skills=${skills}`);
        const result = await response.json();
        
        if (result.success && result.jobs && result.jobs.length > 0) {
            data.job_recommendations = result.jobs;
            localStorage.setItem('analysisData', JSON.stringify(data));
            displayJobRecommendations(data);
            showNotification(`✅ Found ${result.jobs.length} jobs from JSearch!`, 'success');
        } else {
            // Fallback to sample jobs
            data.job_recommendations = getSampleJobs(data);
            displayJobRecommendations(data);
            showNotification('Using sample jobs. Add RapidAPI key for real jobs.', 'info');
        }
    } catch (error) {
        console.error("Error fetching jobs:", error);
        // Fallback to sample jobs
        data.job_recommendations = getSampleJobs(data);
        displayJobRecommendations(data);
        showNotification('Error fetching jobs. Using sample data.', 'error');
    }
    
    if (btn) {
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Jobs';
        btn.disabled = false;
    }
}

// Get Sample Jobs (fallback if API fails)
function getSampleJobs(data) {
    const skills = data.skills_found || [];
    const jobs = [
        {
            title: 'Python Developer',
            company: 'Tech Corp',
            location: 'Bangalore, India',
            salary: '₹8-12 LPA',
            match: 92,
            skills: ['Python', 'Django', 'SQL', 'Git'],
            type: 'Full-time',
            posted: '2024-01-15',
            url: '#',
            portal: 'LinkedIn'
        },
        {
            title: 'Frontend Developer',
            company: 'Web Solutions',
            location: 'Hyderabad, India',
            salary: '₹7-10 LPA',
            match: 88,
            skills: ['React', 'JavaScript', 'HTML', 'CSS'],
            type: 'Full-time',
            posted: '2024-01-16',
            url: '#',
            portal: 'Indeed'
        },
        {
            title: 'Full Stack Developer',
            company: 'Startup Innovations',
            location: 'Remote, India',
            salary: '₹10-15 LPA',
            match: 85,
            skills: ['React', 'Node.js', 'MongoDB', 'Express'],
            type: 'Remote',
            posted: '2024-01-14',
            url: '#',
            portal: 'AngelList'
        }
    ];
    return jobs;
}

// Display Job Recommendations
function displayJobRecommendations(data) {
    const container = document.getElementById('jobRecommendations');
    if (!container) return;
    
    const jobs = data.job_recommendations || [];
    
    if (jobs.length === 0) {
        container.innerHTML = '<div class="text-center py-5"><p class="text-muted">No jobs found matching your profile</p></div>';
        return;
    }
    
    let html = '<div class="row">';
    
    jobs.forEach(job => {
        let matchClass = 'match-high';
        if (job.match < 70) matchClass = 'match-low';
        else if (job.match < 80) matchClass = 'match-medium';
        
        html += `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="job-card">
                    <span class="match-badge ${matchClass}">${job.match}% Match</span>
                    <h5 class="mt-3">${job.title}</h5>
                    <p class="text-primary mb-2">
                        <i class="fas fa-building"></i> ${job.company}
                    </p>
                    <p class="mb-2">
                        <i class="fas fa-map-marker-alt text-muted"></i> ${job.location}<br>
                        <i class="fas fa-money-bill-alt text-muted"></i> ${job.salary}<br>
                        <i class="fas fa-clock text-muted"></i> ${job.posted || 'Recently'}<br>
                        <i class="fas fa-briefcase text-muted"></i> ${job.type || 'Full-time'}
                    </p>
                    <div class="mb-3">
                        ${job.skills.map(s => `<span class="badge bg-light text-dark me-1">${s}</span>`).join('')}
                    </div>
                    <button class="quick-action-btn w-100" onclick="window.open('${job.url || '#'}', '_blank')">
                        <i class="fas fa-external-link-alt"></i> Apply on ${job.portal || 'Job Portal'}
                    </button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Show detailed score breakdown
function showDetailedScore() {
    const data = JSON.parse(localStorage.getItem('analysisData'));
    if (!data) {
        showNotification('Upload resume first', 'error');
        return;
    }
    
    const score = data.score || 0;
    const skills = data.skills_found?.length || 0;
    const roles = data.matched_roles?.length || 0;
    const exp = data.experience_years || 0;
    
    showNotification(
        `📊 Score: ${score}% | Skills: ${skills} | Roles: ${roles} | Experience: ${exp} years`,
        'info'
    );
}

// Show learning resources
function showLearningResources() {
    const data = JSON.parse(localStorage.getItem('analysisData'));
    if (!data || !data.skill_gaps || Object.keys(data.skill_gaps).length === 0) {
        showNotification('No skill gaps to learn! Great job!', 'success');
        return;
    }
    
    // Collect all missing skills
    const missingSkills = new Set();
    Object.values(data.skill_gaps).forEach(skills => {
        skills.forEach(skill => missingSkills.add(skill));
    });
    
    const skillsList = Array.from(missingSkills).join(', ');
    showNotification(`📚 Recommended to learn: ${skillsList}`, 'info');
    
    // Open learning platform
    window.open('https://www.coursera.org', '_blank');
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification {
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        border-radius: 10px;
        font-weight: 500;
        z-index: 9999;
    }
    
    .badge {
        padding: 5px 10px;
        border-radius: 30px;
    }
    
    .skill-badge {
        display: inline-block;
        padding: 8px 16px;
        margin: 5px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .skill-badge:hover {
        transform: scale(1.1);
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }
    
    .skill-badge.technical {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .skill-badge.soft {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .skill-badge.tool {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    .gap-item {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    
    .gap-item:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(255,193,7,0.2);
    }
    
    .gap-role {
        font-weight: 600;
        color: #856404;
        margin-bottom: 10px;
    }
    
    .gap-skill {
        display: inline-block;
        padding: 5px 12px;
        margin: 3px;
        background: white;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        color: #856404;
        border: 1px solid #ffc107;
    }
    
    .job-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .job-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 40px rgba(102,126,234,0.2);
        border-color: #667eea;
    }
    
    .match-badge {
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 5px 15px;
        border-radius: 30px;
        font-weight: 600;
        font-size: 14px;
        color: white;
    }
    
    .match-high { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
    .match-medium { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
    .match-low { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    
    .progress {
        height: 10px;
        border-radius: 5px;
        background: #f0f0f0;
    }
    
    .progress-bar {
        transition: width 0.5s ease;
        border-radius: 5px;
    }
`;
document.head.appendChild(style);