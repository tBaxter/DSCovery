from django.conf import settings
import json
import re
import requests
from bs4 import BeautifulSoup

root_url = 'https://recruiting.paylocity.com'

# Name, key
firms = [
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
                    jobs.append({
                        'company': co_name,
                        'title': card['JobTitle'],
                        'link': root_url + "/Recruiting/Jobs/Details/" + str(card['JobId']),
                        'location': card['LocationName'],
                        'job_id': card['JobId'],
                        'pub_date': card['PublishedDate']
                    })    
    return jobs
 