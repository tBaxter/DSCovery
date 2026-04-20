from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

# headless rendering helper
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

# TeamTailor-powered career sites
# Many TeamTailor pages load jobs dynamically; we'll try regular requests first
# and fall back to a headless browser if necessary.

PRIORITY = 10  # run later than standard importers

firms = [
    ('Bixal', 'https://careers.bixal.com/jobs')
]


def fetch_with_playwright(url):
    if sync_playwright is None:
        raise RuntimeError("playwright not installed")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        html = page.content()
        browser.close()
        return html


def get_jobs():
    jobs = []
    for co_name, url in firms:
        print("Importing", co_name)
        html = None
        try:
            r = requests.get(url, headers=settings.IMPORTER_HEADERS, timeout=10)
            if r.status_code == 200:
                html = r.content
        except Exception as e:
            print("Requests fetch failed for", co_name, e)
        
        # if no html or no jobs found, try headless browser
        if not html:
            try:
                print("Falling back to Playwright for", co_name)
                html = fetch_with_playwright(url).encode('utf-8')
            except Exception as e:
                print("Playwright fetch failed for", co_name, e)
                continue
        
        soup = BeautifulSoup(html, "html.parser")
        # TeamTailor job card selectors
        job_cards = soup.find_all('a', class_='job-card')
        print(f"Selector 1 (job-card): {len(job_cards)} cards")
        
        if not job_cards:
            job_cards = soup.find_all('a', {'data-testid': 'job-listing-item'})
            print(f"Selector 2 (data-testid): {len(job_cards)} cards")
        
        if not job_cards:
            job_cards = soup.select('[class*="job"][class*="card"], [class*="listing"][class*="item"]')
            print(f"Selector 3 (CSS combined): {len(job_cards)} cards")

        if not job_cards:
            print(f"No job cards found for {co_name} (url={url}) - checking HTML for structure clues...")
            # Log some sample HTML to help debug
            all_a_tags = soup.find_all('a', limit=5)
            print(f"Sample links found: {[a.get('class', 'no-class') for a in all_a_tags]}")
            return jobs
        
        for card in job_cards:
            try:
                title_elem = card.find(['h2', 'h3', 'h4']) or card
                title = title_elem.get_text(strip=True) if title_elem else 'Unknown'
                link = card.get('href', '')
                if not link.startswith('http'):
                    link = 'https://careers.bixal.com' + link if link.startswith('/') else link
                location_elem = card.find(class_=lambda x: x and ('location' in x.lower() or 'place' in x.lower()))
                location = location_elem.get_text(strip=True) if location_elem else 'Unknown'
                if title and link:
                    job_id = link.split('/')[-1] if link else None
                    if job_id:
                        jobs.append({
                            'company': co_name,
                            'title': title,
                            'link': link,
                            'location': location,
                            'job_id': job_id,
                            'pub_date': datetime.date.today()
                        })
            except Exception as e:
                print(f"Error parsing job card for {co_name}: {e}")
                continue
    return jobs
