import json
import pytz
import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.conf import settings

root_url = 'https://recruiting.paylocity.com'

# Name, key
firms = [
    ('Amivero', 'c3999ef9-e4cd-4e2f-a5b8-b0bd0facd60a/Amivero'),
    ('eSimplicity', 'a2d790ab-c239-40b9-a6ea-9e5853bbd737/eSimplicity'),
    ('So Company', '1974d707-52df-497d-9c10-b664aec386a3/Storij-Inc-Current-Openings'),
    ('Vaultes', '512b109e-bb46-4419-98e4-84028b520a50/Vaultes-LLC/'),
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
            pass 
        soup = BeautifulSoup(r.content, "html.parser")
        script_tag = soup.find('script', text=re.compile(r'window\.pageData\s*=\s*'))

        if script_tag:
            # Extract the JavaScript content and use regular expression to extract JSON
            script_content = script_tag.string
            match = re.search(r'window\.pageData\s*=\s*(\{.*\});', script_content)

            if match: # Parse the JSON data
                app_data = json.loads(match.group(1))
                job_cards = app_data.get('Jobs', [])

                for card in job_cards:
                    pub_date_str = card['PublishedDate']
                    pub_date = datetime.fromisoformat(pub_date_str)
                    one_week_ago = datetime.now(pytz.utc) - timedelta(days=7)
                    if pub_date >= one_week_ago:
                        jobs.append({
                            'company': co_name,
                            'title': card['JobTitle'],
                            'link': root_url + "/Recruiting/Jobs/Details/" + str(card['JobId']),
                            'location': card['LocationName'],
                            'job_id': card['JobId'],
                            'pub_date': pub_date_str
                        })
    return jobs
 