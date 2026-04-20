from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

from jobsearch.importers.utils import already_in_jobs, fetch_response

root_url = 'https://boards.greenhouse.io/embed/job_board?for='
alternate_url = 'https://job-boards.greenhouse.io/embed/job_board?for='

# Name, GH key
firms = [
    #('BlueLabs', 'bluelabsanalyticsinc'),
    ('Capital Technology Group', 'capitaltg'),
    # ('MetroStar', 'metrostarsystems'), Metrostar floods the site. Don't know how to fix.
    ('PBG Consulting', 'pbgconsultingllc'),
    ('Pluribus Digital', 'pluribusdigital'),
    ('[Simple]', 'simpletechnologysolutions'),
    ('Skylight', 'skylighthq'),
    ('Softrams', "triafederal"),
    ('Inroads', 'inroads'),
    ('Truss', 'trussworksinc'),
]




def get_jobs():
    jobs = []
    for firm in firms:    
        co_name, key = firm
        try:
            print(f"Importing {co_name}")
            url = root_url + key
            r = fetch_response('get', url, importer_name=co_name, headers=settings.IMPORTER_HEADERS)
            if not r:
                print(f"Trying alternate url for {co_name}")
                url = alternate_url + key
                r = fetch_response('get', url, importer_name=co_name, headers=settings.IMPORTER_HEADERS)
                if not r:
                    print(f"Both URLs failed for {co_name}")
                    continue
            
            print(f"Successfully fetched {url} for {co_name}")
            soup = BeautifulSoup(r.content, "html.parser")
            
            # Try multiple selector strategies
            jobs_found = False
            
            # Strategy 1: Original selectors
            sections = soup.find_all('section', class_="level-0")
            print(f"Strategy 1: Found {len(sections)} sections with class='level-0' for {co_name}")
            
            if sections:
                for section in sections:
                    job_cards = section.find_all('div', class_="opening")
                    print(f"  Found {len(job_cards)} openings in section")
                    if job_cards:
                        jobs_found = True
                        # Process job cards...
                        for card in job_cards:
                            try:
                                a_tag = card.find("a")
                                if not a_tag:
                                    continue
                                job_title = a_tag.text.strip()
                                link = a_tag.get('href', '')
                                if not link:
                                    continue
                                
                                location_span = card.find('span', class_="location")
                                location = location_span.text.strip() if location_span else 'Unknown'
                                
                                new_job = {
                                    'company': co_name,
                                    'job_id': link.rsplit('/')[-1],
                                    'title': job_title,
                                    'link': link,
                                    'location': location,
                                    'pub_date': datetime.date.today()
                                }
                                if not already_in_jobs(new_job, jobs):
                                    jobs.append(new_job)
                                    print(f"  Added job: {job_title}")
                            except Exception as e:
                                print(f"  Error parsing job card: {e}")
            
            # Strategy 2: Look for any job links on the page
            if not jobs_found:
                print(f"Strategy 2: Looking for job links for {co_name}")
                # Look for links that contain job-related keywords in href or text
                all_links = soup.find_all('a', href=True)
                job_links = []
                for link in all_links:
                    href = link.get('href', '')
                    text = link.text.strip().lower()
                    href_lower = href.lower()
                    
                    # Skip obviously non-job links
                    if any(skip in href_lower for skip in ['javascript:', 'mailto:', '#', 'tel:']):
                        continue
                    if any(skip in text for skip in ['apply now', 'apply here', 'view all', 'see all', 'more jobs', 'careers', 'about', 'contact', 'privacy', 'terms']):
                        continue
                    
                    # Include links that look job-related
                    if ('job' in href_lower or 'position' in href_lower or 'opening' in href_lower or 
                        'boards.greenhouse.io' in href or 'greenhouse.io' in href):
                        job_links.append(link)
                
                print(f"  Found {len(job_links)} potential job links")
                
                for link in job_links[:20]:  # Limit to avoid spam
                    try:
                        href = link.get('href')
                        title = link.text.strip()
                        
                        if not title or len(title) < 3:
                            # Try to get title from parent elements
                            parent = link.parent
                            if parent and parent.name in ['div', 'li', 'span']:
                                title = parent.text.strip()
                            if not title or len(title) < 3:
                                continue
                        
                        # Clean up title
                        title = title.replace('\n', ' ').replace('\r', ' ').strip()
                        if len(title) > 100:  # Truncate very long titles
                            title = title[:97] + '...'
                        
                        # Skip if it looks like navigation
                        if len(title.split()) > 10:  # Probably not a job title
                            continue
                        
                        new_job = {
                            'company': co_name,
                            'job_id': href.rsplit('/')[-1] if '/' in href else title.replace(' ', '_').lower(),
                            'title': title,
                            'link': href if href.startswith('http') else f"https://boards.greenhouse.io{href}",
                            'location': 'Unknown',
                            'pub_date': datetime.date.today()
                        }
                        if not already_in_jobs(new_job, jobs):
                            jobs.append(new_job)
                            jobs_found = True
                            print(f"  Added job via strategy 2: {title}")
                    except Exception as e:
                        print(f"  Error parsing link: {e}")
            
            # Strategy 3: Look for structured job data
            if not jobs_found:
                print(f"Strategy 3: Looking for structured data for {co_name}")
                # Look for JSON data in script tags
                scripts = soup.find_all('script', string=lambda x: x and ('job' in x.lower() or 'posting' in x.lower()))
                for script in scripts:
                    try:
                        script_text = script.string
                        if 'window.' in script_text and ('jobs' in script_text.lower() or 'postings' in script_text.lower()):
                            print(f"  Found potential job data in script tag")
                            # Could parse JSON here if needed
                    except:
                        pass
            
            if not jobs_found:
                print(f"No jobs found for {co_name} using any strategy")
                
        except Exception as e:
            print(f"Unexpected error processing {co_name}: {e}")
            continue
    
    return jobs
 