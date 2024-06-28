from django.conf import settings
import datetime
import json
import re
import requests
from bs4 import BeautifulSoup

root_url = 'https://jobs.ashbyhq.com'

# Name, GH key
firms = [
    ('All Women Leadership', 'awlstrategies'),
    ('Verdance', 'verdance'),
]

def get_jobs():
    jobs = []
    for firm in firms:
        co_name, key = firm
        print("Importing", co_name)
        url = root_url + '/' + key
        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good requests response: ", r.status_code)
            return 
        soup = BeautifulSoup(r.content, "html.parser")
        script_tag = soup.find('script', text=re.compile(r'window\.__appData\s*=\s*'))
        if script_tag:
            # Extract the JavaScript content
            script_content = script_tag.string
            # Use regular expression to extract the __appData JSON
            match = re.search(r'window\.__appData\s*=\s*(\{.*\});', script_content)

            if match:
                # Parse the JSON data
                app_data_json = match.group(1)
                app_data = json.loads(app_data_json)
                job_cards = app_data.get('jobBoard', {}).get('jobPostings', [])

                for card in job_cards:
                    jobs.append({
                        'company': co_name,
                        'title': card['title'],
                        'link': url + "/" + card['id'], # not jobId
                        'location': card['locationName'],
                        'job_id': card['jobId'],
                        'pub_date': card['publishedDate']
                    })
    return jobs
        