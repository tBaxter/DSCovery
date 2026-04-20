from django.conf import settings
import json
import re
import requests
from bs4 import BeautifulSoup

from jobsearch.importers.utils import fetch_response

root_url = 'https://jobs.ashbyhq.com'

# Name, key
firms = [
    ('All Women Leadership', 'awlstrategies'),
    ('Verdance', 'verdance'),
    ('Mighty Acorn', 'mightyacorn'),
]

try:
    from playwright.sync_api import sync_playwright
    playwright_available = True
except ImportError:
    sync_playwright = None
    playwright_available = False


def get_jobs():
    jobs = []
    
    for firm in firms:
        co_name, key = firm
        print("Importing", co_name)
        url = root_url + '/' + key

        # Try simple scraping first
        try:
            co_jobs = _get_jobs_via_scraping(url, co_name)
            print(f"Scraping found {len(co_jobs)} jobs for {co_name}")
            if co_jobs:
                jobs.extend(co_jobs)
                continue
        except Exception as e:
            print(f"Scraping failed for {co_name}: {e}")
        
        # Fallback to Playwright if available
        if playwright_available:
            try:
                co_jobs = _get_jobs_via_playwright(url, co_name)
                print(f"Playwright found {len(co_jobs)} jobs for {co_name}")
                if co_jobs:
                    jobs.extend(co_jobs)
            except Exception as e:
                print(f"Playwright failed for {co_name}: {e}")
    
    return jobs


def _get_jobs_via_playwright(url, co_name):
    """Get jobs using Playwright to handle dynamic content"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=settings.IMPORTER_HEADERS.get('User-Agent', 'Mozilla/5.0...')
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until='networkidle')
            # Wait for job content to load - try multiple strategies
            page.wait_for_timeout(5000)  # Wait 5 seconds
            
            # Try to wait for specific job-related elements
            try:
                page.wait_for_selector('.job-post, .posting, [data-job-id]', timeout=10000)
                print(f"Found job selector for {co_name}")
            except:
                print(f"No job selectors found within timeout for {co_name}")
            
            # Try to extract from updated __appData
            app_data = page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script'));
                    for (const script of scripts) {
                        const match = script.textContent.match(/window\.__appData\s*=\s*(\{.*\});/);
                        if (match) {
                            try {
                                return JSON.parse(match[1]);
                            } catch (e) {
                                console.log('Failed to parse __appData:', e);
                            }
                        }
                    }
                    return null;
                }
            """)
            
            if app_data and app_data.get('jobBoard') and app_data['jobBoard'].get('jobPostings'):
                print(f"Found job data in __appData for {co_name}")
                job_cards = app_data['jobBoard']['jobPostings']
                jobs = []
                for card in job_cards:
                    jobs.append({
                        'company': co_name,
                        'title': card['title'],
                        'link': url + "/" + card['id'],
                        'location': card.get('locationName', 'Remote'),
                        'job_id': card.get('jobId', card['id']),
                        'pub_date': card.get('publishedDate', '2026-01-01')
                    })
                return jobs
            
            # Fallback to DOM scraping
            job_selectors = [
                '[data-job-id]',
                '.job-post',
                '.posting', 
                '.job-posting',
                '.job-listing',
                '.job-card',
                'a[href*="/job/"]',
                'a[href*="/posting/"]',
                '.jobs-list a',
                '.job-list a'
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector '{selector}' for {co_name}")
                    job_elements.extend(elements)
                    break
            
            print(f"Total job elements found: {len(job_elements)}")
            
            jobs = []
            for element in job_elements:
                try:
                    # Try to extract job data from the element
                    title_elem = element.query_selector('h2, h3, .title, [data-title], a')
                    link_elem = element.query_selector('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.text_content().strip()
                        link = link_elem.get_attribute('href')
                        
                        if link and not link.startswith('http'):
                            link = url.rstrip('/') + link
                        
                        # Extract location if available
                        location_elem = element.query_selector('.location, [data-location], .job-location')
                        location = location_elem.text_content().strip() if location_elem else 'Remote'
                        
                        # Generate job_id from link or title
                        job_id = link.split('/')[-1] if link else title.replace(' ', '_').lower()
                        
                        jobs.append({
                            'company': co_name,
                            'title': title,
                            'link': link,
                            'location': location,
                            'job_id': job_id,
                            'pub_date': '2026-01-01'  # Placeholder date
                        })
                except Exception as e:
                    print(f"Error parsing job element: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            print(f"Playwright error for {co_name}: {e}")
            return []
        finally:
            browser.close()


def _get_jobs_via_scraping(url, co_name):
    """Fallback method using old scraping approach"""
    co_jobs = []  # Initialize jobs list
    
    response = fetch_response('get', url, importer_name=co_name, headers=settings.IMPORTER_HEADERS)
    if response is None:
        return []
    
    soup = BeautifulSoup(response.content, "html.parser")
    script_tag = soup.find('script', text=re.compile(r'window\.__appData\s*=\s*'))
    
    if not script_tag:
        print(f"No __appData script tag found for {co_name} - website structure may have changed")
        return []
    
    script_content = script_tag.string
    match = re.search(r'window\.__appData\s*=\s*(\{.*\});', script_content)

    if not match:
        print(f"Could not extract __appData JSON for {co_name}")
        return []
    
    try:
        app_data_json = match.group(1)
        app_data = json.loads(app_data_json)
    except json.JSONDecodeError as e:
        print(f"Failed to parse __appData JSON for {co_name}: {e}")
        return []
    
    if not app_data or not app_data.get('jobBoard'):
        print(f"No jobBoard data found for {co_name}")
        return []
    
    try:
        job_cards = app_data['jobBoard'].get('jobPostings', [])
        print(f"Found {len(job_cards)} job postings for {co_name} via scraping")
    except Exception as e:
        print(f"Failed to get job cards for {co_name}: {e}")
        return []
    
    for card in job_cards:
        try:
            co_jobs.append({
                'company': co_name,
                'title': card.get('title', ''),
                'link': url + "/" + card.get('id', ''),
                'location': card.get('locationName', 'Remote'),
                'job_id': card.get('jobId', card.get('id', '')),
                'pub_date': card.get('publishedDate', '2026-01-01')
            })
        except Exception as e:
            print(f"Error processing job card for {co_name}: {e}")
            continue
    
    return co_jobs
        