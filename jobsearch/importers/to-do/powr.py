#humango solutions https://www.humangosolutions.com/join-our-team 
#https://www.powr.io/job-board/u/2194a2f4_1705612926#platform=html 
#https://www.powr.io/job-board/i/37800654

#tusk - uses powr. Should be doable. https://www.tuskservices.co/job-board
#https://www.powr.io/job-board/i/33674153


import json
import re

from django.conf import settings
import requests
from bs4 import BeautifulSoup


root_url = 'https://www.powr.io/job-board/i'

# Name, GH key
firms = [
    ('Humango', 'https://www.humangosolutions.com/join-our-team'),
    ('Tusk', 'https://www.tuskservices.co/job-board'),
]


def get_jobs():
    jobs = []
    for firm in firms:    
        co_name, url = firm
        print("Importing", co_name)
        print("url", url)

        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good response for ", co_name, r.status_code)
            pass 
        soup = BeautifulSoup(r.content, "html.parser")
        script_tag = soup.find('script', text=re.compile(r'window\.CONTENT\s*=\s*{.*?};', re.DOTALL))
        print(script_tag)
        if script_tag:
            # Extract the JavaScript content and use regular expression to extract JSON
            script_content = script_tag.string
            match = re.search(r'window\.CONTENT\s*=\s*(\{.*\});', script_content)

            if match: # Parse the JSON data
                app_data = json.loads(match.group(1))
                job_cards = app_data.get('byDepartments', [])
                print(job_cards)

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