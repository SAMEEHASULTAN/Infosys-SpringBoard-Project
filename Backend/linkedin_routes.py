import time
import csv
import os
import re
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

class LinkedInScraper:
    def __init__(self, headless=False):
        """Initialize LinkedIn scraper"""
        print("🔧 Initializing LinkedIn Scraper...")
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # Anti-detection options
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Initialize driver
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome driver initialized")
        except Exception as e:
            print(f"⚠️ Error with ChromeDriverManager: {e}")
            print("Trying direct initialization...")
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.wait = WebDriverWait(self.driver, 10)
        self.data_dir = os.path.join(os.path.dirname(__file__), 'scraped_data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def search_jobs(self, job_titles, location="India", max_jobs=30):
        """Search for jobs on LinkedIn"""
        all_jobs = []
        
        # Convert single string to list if needed
        if isinstance(job_titles, str):
            job_titles = [job_titles]
        
        for job_title in job_titles:
            print(f"\n🔍 Searching: {job_title} in {location}")
            jobs = self._scrape_jobs(job_title, location, max_jobs // len(job_titles))
            all_jobs.extend(jobs)
            time.sleep(random.uniform(3, 6))
        
        if all_jobs:
            self._save_jobs(all_jobs)
        
        return all_jobs
    
    def _scrape_jobs(self, job_title, location, max_jobs):
        """Scrape jobs for specific title"""
        jobs = []
        
        try:
            # LinkedIn job search URL
            search_query = job_title.replace(' ', '%20')
            location_query = location.replace(' ', '%20')
            url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}&location={location_query}"
            
            print(f"🌐 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # Scroll to load jobs
            self._scroll_page()
            
            # Get job cards - try multiple selectors
            job_cards = []
            selectors = [
                ".job-card-container",
                ".job-search-card",
                ".jobs-search-results__list-item",
                "li[data-occludable-job-id]"
            ]
            
            for selector in selectors:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        job_cards = cards
                        print(f"📊 Found {len(cards)} jobs with selector: {selector}")
                        break
                except:
                    continue
            
            if not job_cards:
                print("⚠️ No job cards found")
                return []
            
            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    print(f"  Processing job {i+1}/{min(len(job_cards), max_jobs)}...")
                    
                    # Scroll to card
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(1)
                    
                    # Click on card
                    try:
                        card.click()
                        time.sleep(2)
                    except:
                        print("    ⚠️ Could not click card, trying JavaScript click...")
                        self.driver.execute_script("arguments[0].click();", card)
                        time.sleep(2)
                    
                    job = self._extract_job_details(card)
                    if job:
                        jobs.append(job)
                        print(f"    ✅ {job['title'][:30]} at {job['company'][:20]}")
                    
                except Exception as e:
                    print(f"    ⚠️ Error on job {i+1}: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error in _scrape_jobs: {e}")
        
        return jobs
    
    def _scroll_page(self):
        """Scroll page to load more jobs"""
        for i in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"  📜 Scroll {i+1}/3 complete")
    
    def _extract_job_details(self, card):
        """Extract job details"""
        try:
            # Extract title
            title = self._get_text(card, [
                ".job-card-list__title",
                ".job-title",
                "h3.base-search-card__title",
                "a.job-card-list__title"
            ]) or "Unknown Title"
            
            # Extract company
            company = self._get_text(card, [
                ".job-card-container__company-name",
                ".job-company",
                "h4.base-search-card__subtitle",
                ".job-card-container__link"
            ]) or "Unknown Company"
            
            # Extract location
            location = self._get_text(card, [
                ".job-card-container__metadata-item",
                ".job-location",
                ".job-search-card__location",
                ".job-card-container__metadata-wrapper"
            ]) or "India"
            
            # Get description from detail panel
            description = self._get_description()
            
            # Get URL
            url = self._get_url(card)
            
            # Get posted date
            posted_date = self._get_posted_date(card)
            
            # Extract skills from description (simple keyword matching)
            skills = self._extract_skills(description)
            
            return {
                'title': title.strip(),
                'company': company.strip(),
                'location': location.strip(),
                'description': description[:1000] + "..." if len(description) > 1000 else description,
                'url': url,
                'posted_date': posted_date,
                'skills': skills[:8],  # Top 8 skills
                'source': 'LinkedIn',
                'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"    ⚠️ Error extracting details: {e}")
            return None
    
    def _get_text(self, element, selectors):
        """Safely get text from element"""
        for selector in selectors:
            try:
                found = element.find_element(By.CSS_SELECTOR, selector)
                if found and found.text:
                    return found.text.strip()
            except:
                continue
        return ""
    
    def _get_description(self):
        """Get job description from detail panel"""
        try:
            time.sleep(1)  # Wait for description to load
            desc_selectors = [
                ".description__text",
                ".show-more-less-html__markup",
                ".jobs-description__content",
                ".job-details"
            ]
            
            for selector in desc_selectors:
                try:
                    desc = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if desc and desc.text:
                        return desc.text.strip()
                except:
                    continue
            
            return ""
        except:
            return ""
    
    def _get_url(self, card):
        """Get job URL"""
        try:
            link = card.find_element(By.CSS_SELECTOR, "a")
            return link.get_attribute('href') or "#"
        except:
            return "#"
    
    def _get_posted_date(self, card):
        """Get posting date"""
        try:
            date = self._get_text(card, [
                ".job-card-container__listed-status",
                ".job-search-card__listed-status",
                ".posted-date"
            ])
            return date or "Recently"
        except:
            return "Recently"
    
    def _extract_skills(self, description):
        """Extract skills from description using keyword matching"""
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Vue', 'Node.js',
            'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'AWS', 'Azure', 'GCP',
            'Docker', 'Kubernetes', 'Git', 'Jenkins', 'Machine Learning', 'AI',
            'Data Science', 'HTML', 'CSS', 'Django', 'Flask', 'Spring',
            'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Flutter',
            'Tableau', 'Power BI', 'Excel', 'Communication', 'Leadership'
        ]
        
        found_skills = []
        desc_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in desc_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _save_jobs(self, jobs):
        """Save jobs to JSON and CSV"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_path = os.path.join(self.data_dir, f"linkedin_jobs_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(jobs)} jobs to {json_path}")
        
        # Save latest version
        latest_json = os.path.join(self.data_dir, "linkedin_jobs_latest.json")
        with open(latest_json, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        # Also save as CSV for viewing
        csv_path = os.path.join(self.data_dir, f"linkedin_jobs_{timestamp}.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if jobs:
                writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
                writer.writeheader()
                writer.writerows(jobs)
        
        print(f"✅ Also saved to {csv_path}")
        
        return json_path
    
    def get_latest_jobs(self):
        """Get the latest scraped jobs"""
        latest_json = os.path.join(self.data_dir, "linkedin_jobs_latest.json")
        if os.path.exists(latest_json):
            with open(latest_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")


# Simple matching function (no sklearn needed)
def match_jobs_with_resume(jobs, resume_skills):
    """Match jobs with resume skills using simple keyword matching"""
    if not resume_skills:
        return jobs
    
    for job in jobs:
        # Convert skills to lowercase for matching
        job_skills = [s.lower() for s in job.get('skills', [])]
        resume_skills_lower = [s.lower() for s in resume_skills]
        
        # Count matches
        matches = sum(1 for skill in resume_skills_lower if any(skill in js for js in job_skills))
        
        # Calculate match percentage
        if len(resume_skills) > 0:
            match_percent = min(int((matches / len(resume_skills)) * 100), 98)
        else:
            match_percent = 70
        
        # Also check description for matches
        description = job.get('description', '').lower()
        desc_matches = sum(1 for skill in resume_skills_lower if skill in description)
        
        # Combine both scores
        final_match = min(match_percent + (desc_matches * 2), 98)
        
        job['match_percentage'] = final_match
    
    # Sort by match percentage
    jobs.sort(key=lambda x: x.get('match_percentage', 0), reverse=True)
    
    return jobs


# For testing
if __name__ == "__main__":
    scraper = LinkedInScraper(headless=False)
    try:
        jobs = scraper.search_jobs(
            job_titles=["Python Developer", "Data Scientist"],
            location="India",
            max_jobs=5
        )
        
        print(f"\n📊 Total jobs scraped: {len(jobs)}")
        
        if jobs:
            print("\n📋 Sample job:")
            job = jobs[0]
            print(f"   Title: {job.get('title')}")
            print(f"   Company: {job.get('company')}")
            print(f"   Location: {job.get('location')}")
            print(f"   Skills: {', '.join(job.get('skills', [])[:5])}")
        
        # Test matching with sample skills
        sample_skills = ['Python', 'SQL', 'JavaScript']
        matched = match_jobs_with_resume(jobs, sample_skills)
        print(f"\n✅ Matched {len(matched)} jobs with sample skills")
        
    finally:
        scraper.close()