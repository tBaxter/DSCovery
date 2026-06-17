from django.conf import settings
import datetime
import re
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from jobsearch.importers.utils import already_in_jobs, fetch_response
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

# Name, careers URL
firms = [
    ('Flexion', 'https://jobs.silkroad.com/Flexion/Careers'),
]


def _extract_job_id(href):
    p = urlparse(href)
    qs = parse_qs(p.query)
    if 'jobId' in qs:
        return qs['jobId'][0]
    seg = p.path.rstrip('/').split('/')[-1]
    return seg or href


def get_jobs():
    jobs = []

    for company_name, url in firms:
        r = fetch_response('get', url, importer_name=company_name, headers=settings.IMPORTER_HEADERS)
        if not r:
            continue

        soup = BeautifulSoup(r.content, 'html.parser')

        # Collect candidate anchors that look like job links
        anchors = soup.find_all('a', href=True)
        seen = set()
        for a in anchors:
            href = a['href']
            # skip non-http links and JS handlers
            if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue

            # likely job links contain jobId or job-related path segments
            href_l = href.lower()
            joblink_patterns = ['jobid=', '/job/', '/jobs/', 'job-detail', 'job-detail.aspx', 'jobdetail', '/careers/']
            if not any(p in href_l for p in joblink_patterns):
                # also accept links that include 'openings' or common silkroad job path
                if not any(p in href_l for p in ['/openings', '/position', '/posting']):
                    continue

            title = a.get_text(strip=True)
            if not title:
                continue

            # filter out navigation/footer links like "My Account", "Site Map", etc.
            bad_title_re = re.compile(r'^(my account|site map|help|contact|about|privacy|terms|login|sign in|search|subscribe)$', re.I)
            if bad_title_re.search(title.strip()):
                continue
            if len(title.strip()) < 3:
                continue

            full_link = urljoin(url, href)
            if full_link in seen:
                continue
            seen.add(full_link)

            job_id = _extract_job_id(full_link)

            # Try to get a nearby location string
            location = ''
            parent = a.parent
            if parent:
                loc = parent.find(class_=re.compile('location|city|sr-job__location|job-location'), recursive=False)
                if loc:
                    location = loc.get_text(strip=True)
            if not location:
                # fallback: next small text node
                nxt = a.find_next(string=True)
                if nxt and len(nxt.strip()) < 100:
                    location = nxt.strip()

            new_job = {
                'company': company_name,
                'job_id': job_id,
                'title': title,
                'link': full_link,
                'location': location,
                'pub_date': datetime.date.today(),
            }

            if not already_in_jobs(new_job, jobs):
                jobs.append(new_job)

        # If we found nothing via plain HTTP, try a Playwright render (some SilkRoad
        # sites render job listings client-side).
        if not jobs and sync_playwright is not None:
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, timeout=60000)
                    try:
                        page.wait_for_selector('a[href*="job"]', timeout=15000)
                    except Exception:
                        pass
                    html = page.content()
                    browser.close()
                soup = BeautifulSoup(html, 'html.parser')

                # repeat parsing on rendered HTML
                anchors = soup.find_all('a', href=True)
                seen = set()
                for a in anchors:
                    href = a['href']
                    if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                        continue
                    href_l = href.lower()
                    if not any(pat in href_l for pat in joblink_patterns):
                        if not any(pat in href_l for pat in ['/openings', '/position', '/posting']):
                            continue
                    title = a.get_text(strip=True)
                    if not title:
                        continue
                    if bad_title_re.search(title.strip()):
                        continue
                    if len(title.strip()) < 3:
                        continue
                    full_link = urljoin(url, href)
                    if full_link in seen:
                        continue
                    seen.add(full_link)
                    job_id = _extract_job_id(full_link)
                    location = ''
                    parent = a.parent
                    if parent:
                        loc = parent.find(class_=re.compile('location|city|sr-job__location|job-location'), recursive=False)
                        if loc:
                            location = loc.get_text(strip=True)
                    if not location:
                        nxt = a.find_next(string=True)
                        if nxt and len(nxt.strip()) < 100:
                            location = nxt.strip()
                    new_job = {
                        'company': company_name,
                        'job_id': job_id,
                        'title': title,
                        'link': full_link,
                        'location': location,
                        'pub_date': datetime.date.today(),
                    }
                    if not already_in_jobs(new_job, jobs):
                        jobs.append(new_job)
            except Exception:
                pass

    return jobs
