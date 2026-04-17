from django.conf import settings
import requests
from jobsearch.importers.utils import already_in_jobs

# Name, Workable company key
firms = [
    ('Blue Tiger', 'blue-tiger'),
    ('Friends From The City', 'friends-from-the-city'),
    ('Pixel Creative', 'pixel-creative'),
    ('Public Digital', 'public-digital-1'),
]

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


def _format_location(location, remote):
    if not isinstance(location, dict):
        return 'Remote' if remote else ''

    parts = []
    city = location.get('city')
    region = location.get('region')
    country = location.get('country')

    if city:
        parts.append(city)
    if region:
        parts.append(region)
    if country and country not in parts:
        parts.append(country)

    if parts:
        return ', '.join(parts)
    if remote:
        return 'Remote'
    return ''


def _build_job_link(company_key, job):
    shortcode = job.get('shortcode') or job.get('code')
    if shortcode:
        return f'https://apply.workable.com/{company_key}/j/{shortcode}'

    if job.get('id'):
        return f'https://apply.workable.com/{company_key}/jobs/{job.get("id")}'

    return f'https://apply.workable.com/{company_key}'


def _fetch_jobs_via_api(company_key):
    url = f'https://apply.workable.com/api/v3/accounts/{company_key}/jobs'
    headers = {
        **settings.IMPORTER_HEADERS,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    try:
        response = requests.post(url, headers=headers, json={}, timeout=15)
        if response.status_code != 200:
            return None

        payload = response.json()
        if not isinstance(payload, dict):
            return None
        return payload.get('results', []) or []
    except Exception:
        return None


def _fetch_jobs_via_playwright(company_key):
    if sync_playwright is None:
        return []

    jobs_data = []
    api_path = f'/api/v3/accounts/{company_key}/jobs'

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()

        def on_response(response):
            if api_path in response.url and response.status == 200:
                try:
                    payload = response.json()
                except Exception:
                    return

                if isinstance(payload, dict):
                    results = payload.get('results', [])
                    if isinstance(results, list):
                        jobs_data.extend(results)

        context.on('response', on_response)
        page = context.new_page()
        page.set_extra_http_headers(settings.IMPORTER_HEADERS)

        try:
            page.goto(f'https://apply.workable.com/{company_key}', wait_until='networkidle')
            page.wait_for_timeout(4000)
        except Exception:
            pass
        finally:
            browser.close()

    return jobs_data


def get_jobs():
    jobs = []

    for company_name, company_key in firms:
        print('Importing', company_name)

        job_cards = _fetch_jobs_via_api(company_key)
        if job_cards is None:
            print('  Direct API unavailable; falling back to Playwright for', company_key)
            job_cards = _fetch_jobs_via_playwright(company_key)

        if not job_cards:
            continue

        for card in job_cards:
            title = card.get('title') or card.get('name') or ''
            if not title:
                continue

            location_source = card.get('location') or (card.get('locations') or [])
            if isinstance(location_source, list) and location_source:
                location_source = location_source[0]

            location = _format_location(location_source, card.get('remote', False))
            link = _build_job_link(company_key, card)
            job_id = str(card.get('id') or card.get('shortcode') or '')
            pub_date = card.get('published') or card.get('publishedDate') or ''

            new_job = {
                'company': company_name,
                'job_id': job_id,
                'title': title,
                'link': link,
                'location': location,
                'pub_date': pub_date,
            }

            if not already_in_jobs(new_job, jobs):
                jobs.append(new_job)

    return jobs
