from django.conf import settings
import datetime
from bs4 import BeautifulSoup

from jobsearch.importers.utils import already_in_jobs, fetch_response, map_section_to_practice

# headless rendering helper
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

# TeamTailor-powered career sites.
# Jobs are rendered client-side in JS; we try plain HTTP first and fall back
# to a headless Playwright browser when no listings are found.
PRIORITY = 10  # run after all standard importers

firms = [
    ('Bixal', 'https://careers.bixal.com/jobs'),
]


def fetch_with_playwright(url):
    if sync_playwright is None:
        raise RuntimeError(
            "playwright is not installed — run: pipenv run python -m playwright install"
        )
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        # Wait for at least one job link to appear before grabbing HTML
        try:
            page.wait_for_selector('a[href*="/jobs/"]', timeout=15000)
        except Exception:
            pass  # grab whatever rendered
        html = page.content()
        browser.close()
    return html


def get_jobs():
    jobs = []

    for co_name, url in firms:
        print(f"Importing {co_name}")
        html = None

        # --- attempt 1: plain HTTP ---
        try:
            r = fetch_response(
                'get', url,
                importer_name=co_name,
                headers=settings.IMPORTER_HEADERS,
                timeout=10,
            )
            if r:
                html = r.content
        except Exception as e:
            print(f"  HTTP fetch failed for {co_name}: {e}")

        soup = BeautifulSoup(html or b'', 'html.parser')

        # TeamTailor job links all live under /jobs/<id>-<slug>
        # Quick check: if we got any, we're done with HTTP.
        job_links = _find_job_links(soup, url)

        # --- attempt 2: Playwright fallback ---
        if not job_links:
            print(f"  No jobs found via HTTP — falling back to Playwright for {co_name}")
            try:
                html = fetch_with_playwright(url).encode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                job_links = _find_job_links(soup, url)
            except Exception as e:
                print(f"  Playwright fetch failed for {co_name}: {e}")
                continue

        if not job_links:
            print(f"  No job listings found for {co_name} after all attempts.")
            continue

        print(f"  Found {len(job_links)} job(s) for {co_name}")

        base_url = url.rsplit('/jobs', 1)[0]  # e.g. https://careers.bixal.com

        for anchor in job_links:
            try:
                href = anchor.get('href', '')
                if not href:
                    continue
                if not href.startswith('http'):
                    href = base_url + href

                # job_id is the numeric prefix before the slug: 576780-mobile-…
                slug = href.rstrip('/').split('/')[-1]
                job_id = slug.split('-')[0] if slug else None
                if not job_id:
                    continue

                # Title: prefer a heading inside the card, fall back to link text
                title_elem = anchor.find(['h2', 'h3', 'h4', 'span'])
                title = (title_elem or anchor).get_text(strip=True)
                if not title:
                    continue

                # Location: TeamTailor often puts it in a <p> or element with
                # "location" / "workplace" / "remote" in the class name.
                location = _extract_text_by_class(anchor, ('location', 'workplace', 'remote', 'place'))

                # Department / role: used to derive job_type
                department = _extract_text_by_class(anchor, ('department', 'role', 'team', 'category'))
                job_type = map_section_to_practice(department or title)

                new_job = {
                    'company': co_name,
                    'job_id': job_id,
                    'title': title,
                    'link': href,
                    'location': location or 'Unknown',
                    'pub_date': datetime.date.today(),
                    'job_type': job_type,
                }

                if not already_in_jobs(new_job, jobs):
                    jobs.append(new_job)

            except Exception as e:
                print(f"  Error parsing job card for {co_name}: {e}")
                continue

    return jobs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_job_links(soup, listing_url):
    """
    Return all <a> tags whose href points to an individual job page.
    TeamTailor job URLs follow the pattern  /jobs/<numeric-id>-<slug>
    """
    base = listing_url.rsplit('/jobs', 1)[0]  # https://careers.bixal.com
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        # normalise relative URLs
        if href.startswith('/'):
            href = base + href
        # must be a job detail page on the same domain
        if '/jobs/' in href and href != listing_url:
            # exclude the listing page itself and pagination links
            slug_part = href.rstrip('/').split('/jobs/')[-1]
            # valid slug starts with digits
            if slug_part and slug_part[0].isdigit():
                links.append(a)
    return links


def _extract_text_by_class(element, keywords):
    """
    Find the first child element whose class attribute contains any of the
    given keywords (case-insensitive) and return its stripped text.
    """
    for tag in element.find_all(True):
        classes = ' '.join(tag.get('class') or []).lower()
        if any(kw in classes for kw in keywords):
            text = tag.get_text(strip=True)
            if text:
                return text
    return ''