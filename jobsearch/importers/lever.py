from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup
from jobsearch.importers.utils import fetch_response


root_url = 'https://jobs.lever.co'

# Name,  key
firms = [
    ('Corbalt', 'corbalt'),
    ('Exygy', 'exygy'),
    ('MO Studio', 'MOstudio'),
    #('Nava', 'nava'),
    ('Skyward', 'skywarditsolutions'),
    ('BLEN', 'blencorp'),
    ('Bellese', 'bellese'),
]


def get_jobs():
    jobs = []
    for firm in firms:
        co_name, key = firm
        # print("Importing", co_name)
        url = root_url + '/' + key

        r = fetch_response('get', url, importer_name=co_name, headers=settings.IMPORTER_HEADERS)
        if not r:
            continue
        soup = BeautifulSoup(r.content, "html.parser")
        job_wrapper = soup.find('div', class_='postings-wrapper')
        if job_wrapper:
            job_cards = job_wrapper.find_all('div', class_="posting")
            for card in job_cards:
                title = card.find('a', class_='posting-title')
                jobs.append({
                    'company': co_name,
                    'title': card.find('h5').text.strip(),
                    'link':  title['href'],
                    'location': card.find('span', class_="workplaceTypes").text.strip(),
                    'job_id': title['href'].rsplit('/')[-1],
                    'pub_date': datetime.date.today()
                })
    return jobs



        