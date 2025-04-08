import json
import pytz
import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.conf import settings

# Company specific information
COMPANY_NAME = "Snowbird Agility"
PAYLOCITY_KEY = "7f253d89-50c7-45db-981f-2eb478344672/Snowbird-Agility"

# Paylocity root URL
ROOT_URL = 'https://recruiting.paylocity.com'


def get_jobs():
    """
    Fetches job listings from Snowbird Agility's Paylocity job board.
    
    Returns:
        list: A list of dictionaries containing job information.
    """
    print(f"Importing {COMPANY_NAME}")
    
    # Construct the full URL for the company's job listings
    url = f"{ROOT_URL}/recruiting/jobs/All/{PAYLOCITY_KEY}"
    
    # Make the HTTP request
    r = requests.get(url, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        print(f"Failed to get good response for {COMPANY_NAME}: {r.status_code}")
        return []
    
    # Parse the HTML response
    soup = BeautifulSoup(r.content, "html.parser")
    
    # Find the script tag containing job data
    script_tag = soup.find('script', text=re.compile(r'window\.pageData\s*=\s*'))
    
    # Initialize empty jobs list
    jobs = []
    
    if script_tag:
        # Extract the JavaScript content
        script_content = script_tag.string
        
        # Use regex to extract the JSON data
        match = re.search(r'window\.pageData\s*=\s*(\{.*\});', script_content)
        
        if match:
            # Parse the JSON data
            app_data = json.loads(match.group(1))
            job_cards = app_data.get('Jobs', [])
            
            # Process each job listing
            for card in job_cards:
                pub_date_str = card['PublishedDate']
                pub_date = datetime.fromisoformat(pub_date_str)
                
                # Snowbird Agility indicated their jobs don't expire, but we'll
                # still filter for recent jobs to avoid overwhelming the system
                one_month_ago = datetime.now(pytz.utc) - timedelta(days=30)
                if pub_date >= one_month_ago:
                    jobs.append({
                        'company': COMPANY_NAME,
                        'title': card['JobTitle'],
                        'link': f"{ROOT_URL}/Recruiting/Jobs/Details/{card['JobId']}",
                        'location': card['LocationName'],
                        'job_id': card['JobId'],
                        'pub_date': pub_date_str
                    })
    
    return jobs


# For testing purposes
if __name__ == "__main__":
    # This will only run if this file is executed directly
    # It won't run when imported as a module
    from pprint import pprint
    
    # Mock the settings for testing
    if not hasattr(settings, 'IMPORTER_HEADERS'):
        class MockSettings:
            IMPORTER_HEADERS = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        settings = MockSettings()
    
    # Get and print the jobs
    print(f"Testing job importer for {COMPANY_NAME}...")
    results = get_jobs()
    print(f"Found {len(results)} jobs:")
    pprint(results)
