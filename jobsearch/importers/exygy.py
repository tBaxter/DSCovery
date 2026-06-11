import datetime
import requests
from bs4 import BeautifulSoup

from jobsearch.importers.utils import already_in_jobs, fetch_response

root_url = 'https://exygy.com'
careers_url = f'{root_url}/careers'


def extract_job_links(soup):
    # Find all anchor tags in the Open Roles section.
    # New Exygy careers pages use relative './job-listings/...' URLs.
    job_links = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href:
            continue

        # Normalize relative paths to absolute URLs.
        if href.startswith('./'):
            href = root_url + href[1:]
        elif href.startswith('/'):
            href = root_url + href
        elif href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
        elif not href.startswith('http'):
            href = root_url + '/' + href.lstrip('./')

        # Only consider job detail links under the new job-listings section.
        if '/job-listings/' not in href:
            continue

        text = a.get_text(strip=True)
        if text and len(text) < 100:
            job_links.append((href, text))
    return job_links


def extract_job_details(job_url):
    r = fetch_response('get', job_url, importer_name='Exygy')
    if not r:
        return None
    soup = BeautifulSoup(r.content, 'html.parser')
    # Title: try h1, fallback to meta
    title = ''
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text(strip=True)
    if not title:
        meta = soup.find('meta', property='og:title')
        if meta:
            title = meta.get('content', '')
    # Description: try main content
    desc = ''
    main = soup.find('main')
    if main:
        desc = main.get_text('\n', strip=True)
    else:
        desc = soup.get_text('\n', strip=True)
    # Location: look for 'remote' or USA
    location = 'Remote, USA'
    # Job ID: from URL
    job_id = job_url.rstrip('/').rsplit('/', 1)[-1]
    # Date: not present, use today
    pub_date = datetime.date.today()
    # Job type: guess from title
    job_type = map_job_type(title)
    return {
        'company': 'Exygy',
        'title': title,
        'link': job_url,
        'location': location,
        'job_id': f'exygy-{job_id}',
        'pub_date': pub_date,
        'details': desc,
        'job_type': job_type,
    }


def map_job_type(title):
    title = title.lower()
    if 'design' in title or 'ux' in title or 'ui' in title:
        return 'design'
    if 'engineer' in title or 'developer' in title:
        return 'engineering'
    if 'product' in title:
        return 'product'
    if 'data' in title:
        return 'data'
    if 'marketing' in title or 'content' in title:
        return 'content'
    return 'other'


def get_jobs():
    jobs = []
    r = fetch_response('get', careers_url, importer_name='Exygy')
    if not r:
        return jobs
    soup = BeautifulSoup(r.content, 'html.parser')
    job_links = extract_job_links(soup)
    for job_url, _ in job_links:
        job = extract_job_details(job_url)
        if job and not already_in_jobs(job, jobs):
            jobs.append(job)
    return jobs
