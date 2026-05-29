from django.conf import settings
import datetime
import time

from jobsearch.importers.utils import already_in_jobs, fetch_response, map_section_to_practice

# Phenom People ("Phenom") powered career sites.
#
# Phenom renders jobs entirely in JS on the public page, but exposes an
# internal POST /widgets endpoint that returns JSON — no OAuth required.
#
# How the endpoint works
# ----------------------
# POST https://<domain>/widgets
# Body: JSON payload with ddoKey="refineSearch" and company-specific refNum
#
# Finding refNum
# --------------
# It is embedded in CDN asset paths on the career site, e.g.:
#   https://pp-cdn.phenompeople.com/CareerConnectResources/prod/FMDFABUS/...
# The all-caps token between "prod/" and the next "/" is the refNum.
#
# Response shape (simplified)
# ---------------------------
# {
#   "refineSearch": {
#     "totalHits": 42,
#     "data": {
#       "jobs": [
#         {
#           "title": "...",
#           "applyUrl": "...",          # full URL to job detail page
#           "jobId": "...",             # ATS req id, e.g. FMDFABUSP100175ENUS
#           "city": "...",
#           "state": "...",
#           "country": "...",
#           "category": "...",         # e.g. "Engineering, IT & Systems Administration"
#           "type": "...",             # Full-time / Part-time / Contract
#         },
#         ...
#       ]
#     }
#   }
# }

PRIORITY = 5  # standard priority; no Playwright needed

PAGE_SIZE = 100  # Phenom supports up to 100 per page

firms = [
    (
        'Fearless',
        'jobs.fearless.com',
        'FMDFABUS',
        'en_us',
    ),
    # To add more Phenom-powered firms:
    # ('Company Name', 'jobs.example.com', 'REFNUM', 'en_us'),
]


def _build_payload(ref_num: str, lang: str, offset: int = 0) -> dict:
    return {
        "lang": lang,
        "deviceType": "desktop",
        "country": "us",
        "pageName": "search-results",
        "size": PAGE_SIZE,
        "from": offset,
        "jobs": True,
        "counts": True,
        "all_fields": ["category", "country", "city", "state", "type"],
        "clearAll": False,
        "jdsource": "facets",
        "isSliderEnable": False,
        "pageId": "page20",
        "siteType": "external",
        "keywords": "",
        "global": False,
        "selected_fields": {},
        "sort": {"order": "desc", "field": "postedDate"},
        "locationData": {},
        "refNum": ref_num,
        "ddoKey": "refineSearch",
    }


def get_jobs():
    jobs = []

    for co_name, domain, ref_num, lang in firms:
        print(f"Importing {co_name} (Phenom / {domain})")
        url = f"https://{domain}/widgets"

        offset = 0
        total = None

        while True:
            payload = _build_payload(ref_num, lang, offset)

            r = fetch_response(
                'post',
                url,
                importer_name=co_name,
                headers={
                    **settings.IMPORTER_HEADERS,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                json=payload,
                timeout=15,
            )

            if not r:
                print(f"  No response from {co_name} at offset {offset}")
                break

            try:
                data = r.json()
            except Exception as e:
                print(f"  JSON parse error for {co_name}: {e}")
                break

            result = data.get('refineSearch', {})

            if total is None:
                total = result.get('totalHits', 0)
                print(f"  {total} total job(s) found")

            job_list = result.get('data', {}).get('jobs', [])
            if not job_list:
                break

            for job in job_list:
                try:
                    title = job.get('title', '').strip()
                    if not title:
                        continue

                    # Phenom job URLs look like:
                    #   https://jobs.fearless.com/us/en/job/FMDFABUSP100175ENUS/Mobile-Developer
                    # applyUrl may already be absolute; jobId gives us the unique key.
                    link = job.get('applyUrl', '').strip()
                    job_id = job.get('jobId', '').strip()

                    if not link or not job_id:
                        continue

                    # Location: prefer city+state, fall back to country
                    city = job.get('city', '').strip()
                    state = job.get('state', '').strip()
                    country = job.get('country', '').strip()
                    if city and state:
                        location = f"{city}, {state}"
                    elif city:
                        location = city
                    elif state:
                        location = state
                    else:
                        location = country or 'Unknown'

                    # Category maps cleanly to job_type
                    category = job.get('category', '')
                    job_type = map_section_to_practice(category or title)

                    new_job = {
                        'company': co_name,
                        'job_id': job_id,
                        'title': title,
                        'link': link,
                        'location': location,
                        'pub_date': datetime.date.today(),
                        'job_type': job_type,
                    }

                    if not already_in_jobs(new_job, jobs):
                        jobs.append(new_job)

                except Exception as e:
                    print(f"  Error parsing job for {co_name}: {e}")
                    continue

            offset += len(job_list)
            if offset >= total:
                break

            time.sleep(0.5)  # be polite between pages

        print(f"  Imported {sum(1 for j in jobs if j['company'] == co_name)} job(s) for {co_name}")

    return jobs
