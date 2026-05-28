import datetime
from bs4 import BeautifulSoup
from jobsearch.importers.utils import already_in_jobs, fetch_response

root_url = 'https://forpeople.us'
careers_url = f'{root_url}/careers'

def extract_job_links(soup):
    job_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Only consider links that look like job pages
        if href.startswith('/careers/') and len(href) > len('/careers/'):  # skip main careers page
            text = a.get_text(strip=True)
            if text and len(text) < 100:
                job_links.append((root_url + href, text))
    return job_links

def extract_job_details(job_url):
    r = fetch_response('get', job_url, importer_name='For People')
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
    # Location: look for 'Remote' or 'United States' in page
    location = 'Remote, USA'
    # Job ID: from URL
    job_id = job_url.rstrip('/').rsplit('/', 1)[-1]
    # Date: not present, use today
    pub_date = datetime.date.today()
    # Job type: guess from title
    job_type = map_job_type(title)
    return {
        'company': 'For People',
        'title': title,
        'link': job_url,
        'location': location,
        'job_id': f'forpeople-{job_id}',
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
    r = fetch_response('get', careers_url, importer_name='For People')
    if not r:
        return jobs
    soup = BeautifulSoup(r.content, 'html.parser')
    job_links = extract_job_links(soup)
    for job_url, _ in job_links:
        job = extract_job_details(job_url)
        if job and not already_in_jobs(job, jobs):
            jobs.append(job)
    return jobs
