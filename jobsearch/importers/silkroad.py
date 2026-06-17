from django.conf import settings
import datetime
import re
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from jobsearch.importers.utils import already_in_jobs, fetch_response

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
            # likely job links contain "Careers" or "Job" in the path/query
            if '/Careers/' not in href and 'job' not in href.lower():
                continue

            title = a.get_text(strip=True)
            if not title:
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

    return jobs
