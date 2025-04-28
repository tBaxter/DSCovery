import datetime
import requests
from bs4 import BeautifulSoup
import os
import sys

# Default headers for requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Try to import already_in_jobs utility or define it if not available
try:
    from django.conf import settings
    DJANGO_AVAILABLE = True
    try:
        HEADERS = getattr(settings, 'IMPORTER_HEADERS', DEFAULT_HEADERS)
    except Exception:
        # If settings aren't properly configured, use default headers
        HEADERS = DEFAULT_HEADERS
        DJANGO_AVAILABLE = False
except (ImportError, ModuleNotFoundError):
    DJANGO_AVAILABLE = False
    HEADERS = DEFAULT_HEADERS
    
# Define a local version of already_in_jobs if not available
if DJANGO_AVAILABLE:
    try:
        from jobsearch.importers.utils import already_in_jobs
    except (ImportError, ModuleNotFoundError):
        def already_in_jobs(job, jobs_list):
            """Check if job already exists in jobs list based on job_id and company."""
            for existing_job in jobs_list:
                if existing_job.get('job_id') == job.get('job_id') and existing_job.get('company') == job.get('company'):
                    return True
            return False
else:
    def already_in_jobs(job, jobs_list):
        """Check if job already exists in jobs list based on job_id and company."""
        for existing_job in jobs_list:
            if existing_job.get('job_id') == job.get('job_id') and existing_job.get('company') == job.get('company'):
                return True
        return False

root_url = 'https://boards.greenhouse.io/embed/job_board?for='

# Name, GH key
firms = [
    ('BlueLabs', 'bluelabsanalyticsinc'),
    ('Capital Technology Group', 'capitaltg'),
    ('Fearless', 'fearless'),
    #('MetroStar', 'metrostarsystems'),
    ('PBG Consulting', 'pbgconsultingllc'),
    ('Pluribus Digital', 'pluribusdigital'),
    ('[Simple]', 'simpletechnologysolutions'),
    ('Skylight', 'skylighthq'),
    ('Inroads', 'inroads')
]

def get_jobs():
    jobs = []
    for firm in firms:    
        co_name, key = firm
        print("Importing", co_name)
        url = root_url + key
        r = requests.get(url, headers=HEADERS)
        
        # If the embedded version fails, try the direct HTML version
        if r.status_code != 200:
            print(f"Embedded board failed for {co_name}, trying direct HTML board")
            direct_url = f'https://boards.greenhouse.io/{key}'
            r = requests.get(direct_url, headers=HEADERS)
            if r.status_code != 200:
                print(f"Failed to get good response for {co_name}: {r.status_code}")
                continue
                
            # Parse the direct HTML version
            soup = BeautifulSoup(r.content, "html.parser")
            job_cards = soup.find_all("div", class_="opening")
            
            if not job_cards:
                # Try alternative selectors for the job cards
                job_cards = soup.select(".job")
                if not job_cards:
                    job_cards = soup.select(".career-board-job-listing")
            
            print(f"Found {len(job_cards)} job cards for {co_name}")
            
            for card in job_cards:
                title_tag = card.find("a")
                if not title_tag:
                    continue
                    
                job_title = title_tag.text.strip()
                link = title_tag["href"]
                
                # Ensure the link is absolute
                if not link.startswith("http"):
                    link = f"https://boards.greenhouse.io{link}"
                
                # Look for location
                location_tag = card.find("span", class_="location")
                if location_tag:
                    location = location_tag.text.strip()
                else:
                    # Try other location selectors
                    location_tag = card.find_next_sibling("span", class_="location")
                    location = location_tag.text.strip() if location_tag else "Unknown"
                
                new_job = {
                    'company': co_name,
                    'job_id': link.rsplit("/", 1)[-1],
                    'title': job_title,
                    'link': link,
                    'location': location,
                    'pub_date': datetime.date.today()
                }
                
                print(f"Found job: {job_title} in {location}")
                
                if not already_in_jobs(new_job, jobs):
                    jobs.append(new_job)
                else:
                    print(f"Job already exists for {co_name} and {job_title}")
                    
            continue
    
        # Original embedded parsing logic
        soup = BeautifulSoup(r.content, "html.parser")
        sections = soup.find_all('section', class_="level-0")
        
        if not sections:
            print(f"No sections found for {co_name}, trying alternative approach")
            # Try alternative parsing for embedded boards that don't use sections
            job_cards = soup.find_all('div', class_="opening")
            for card in job_cards:
                job_title = card.find("a").text.strip() if card.find("a") else ""
                if not job_title:
                    continue
                    
                link = card.find('a')['href'] if card.find('a') else ""
                if not link:
                    continue
                    
                location_tag = card.find('span', class_="location")
                location = location_tag.text.strip() if location_tag else "Unknown"
                
                new_job = {
                    'company': co_name,
                    'job_id': link.rsplit('/')[-1],
                    'title': job_title,
                    'link': link,
                    'location': location,
                    'pub_date': datetime.date.today()
                }
                
                print(f"Found job: {job_title} in {location}")
                
                if not already_in_jobs(new_job, jobs):
                    jobs.append(new_job)
                else:
                    print(f"Job already exists for {co_name} and {job_title}")
            
            continue
            
        for section in sections:
            try:
                section_title = section.find('h3').text.strip()
            except:
                # but some people put it in an H2, and if we can't find one at all, we still need a value.
                try:
                    section_title = section.find('h2').text.strip() if section.find('h2') else ''
                except:
                    section_title = ''
                    
            # now get the cards for that section
            job_cards = section.find_all('div', class_="opening")
            for card in job_cards:
                try:
                    job_title = card.find("a").text.strip()
                except (AttributeError, TypeError):
                    continue
                    
                try:
                    title = f"{section_title}: {job_title}" if section_title else job_title
                except Exception:
                    title = job_title
                    
                try:
                    link = card.find('a')['href']
                except (AttributeError, TypeError, KeyError):
                    continue
                    
                location_tag = card.find('span', class_="location")
                location = location_tag.text.strip() if location_tag else "Unknown"
                
                new_job = {
                    'company': co_name,
                    'job_id': link.rsplit('/')[-1],
                    'title': title,
                    'link': link,
                    'location': location,
                    'pub_date': datetime.date.today()
                }
                
                print(f"Found job: {title} in {location}")
                
                if not already_in_jobs(new_job, jobs):
                    jobs.append(new_job)
                else:
                    print(f"Job already exists for {co_name} and {title}")
    
    print(f"Total jobs found: {len(jobs)}")
    return jobs

if __name__ == "__main__":
    # Test the scraper
    company_jobs = get_jobs()
    print(f"Found {len(company_jobs)} total jobs:")
    for job in company_jobs:
        print(f"- {job['title']} at {job['company']} in {job['location']}")