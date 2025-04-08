import json
import pytz
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Safely handle Django settings or mock them
try:
    from django.conf import settings
    _ = settings.IMPORTER_HEADERS  # Force access to trigger exception if not configured
except Exception:
    from types import SimpleNamespace
    settings = SimpleNamespace()
    settings.IMPORTER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }


root_url = 'https://recruiting.paylocity.com'

# Name, key
firms = [
    ('Amivero', 'c3999ef9-e4cd-4e2f-a5b8-b0bd0facd60a/Amivero'),
    ('eSimplicity', 'a2d790ab-c239-40b9-a6ea-9e5853bbd737/eSimplicity'),
    ('So Company', '1974d707-52df-497d-9c10-b664aec386a3/Storij-Inc-Current-Openings'),
    ('Vaultes', '512b109e-bb46-4419-98e4-84028b520a50/Vaultes-LLC/'),
    ('Snowbird Agility', '7f253d89-50c7-45db-981f-2eb478344672/Snowbird-Agility'),
]


def get_jobs():
    jobs = []
    for firm in firms:    
        co_name, key = firm
        print("Importing", co_name)
        url = root_url + '/recruiting/jobs/All/' + key

        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good response for ", co_name, r.status_code)
            continue
        
        soup = BeautifulSoup(r.content, "html.parser")
        script_tag = soup.find('script', text=re.compile(r'window\.pageData\s*=\s*'))

        if script_tag:
            script_content = script_tag.string
            match = re.search(r'window\.pageData\s*=\s*(\{.*\});', script_content)

            if match:
                app_data = json.loads(match.group(1))
                job_cards = app_data.get('Jobs', [])

                for card in job_cards:
                    print(f"Raw published date: {card['PublishedDate']}")
                    pub_date_str = card['PublishedDate']
                    pub_date = datetime.fromisoformat(pub_date_str).astimezone(pytz.utc)
                    one_week_ago = datetime.now(pytz.utc) - timedelta(days=7)
                    if pub_date >= one_week_ago:
                        job = {
                            'company': co_name,
                            'title': card['JobTitle'],
                            'link': root_url + "/Recruiting/Jobs/Details/" + str(card['JobId']),
                            'location': card['LocationName'],
                            'job_id': card['JobId'],
                            'pub_date': pub_date_str
                        }
                        print(f"✅ Keeping job: {job['title']} ({job['location']})")
                        jobs.append(job)
    return jobs

 
# For testing purposes
if __name__ == "__main__":
    # Set up a basic IMPORTER_HEADERS for testing
    import sys
    from types import SimpleNamespace
    
    # Create a mock settings object with the headers we need
    mock_settings = SimpleNamespace()
    mock_settings.IMPORTER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Save the original settings
    if 'django.conf' in sys.modules and hasattr(sys.modules['django.conf'], 'settings'):
        original_settings = sys.modules['django.conf'].settings
    else:
        original_settings = None
    
    # Replace with our mock settings
    if 'django.conf' in sys.modules:
        sys.modules['django.conf'].settings = mock_settings
    
    try:
        # Run the scraper
        print("Testing Paylocity scraper...")
        all_jobs = get_jobs()
        
        # Filter for Snowbird Agility
        snowbird_jobs = [job for job in all_jobs if job['company'] == 'Snowbird Agility']
        print(f"Found {len(snowbird_jobs)} Snowbird Agility jobs:")
        for job in snowbird_jobs:
            print(f"- {job['title']} ({job['location']})")
    finally:
        try:
            if original_settings and 'django.conf' in sys.modules:
                sys.modules['django.conf'].settings = original_settings
        except Exception as e:
            print("⚠️ Skipped resetting Django settings due to:", str(e))
