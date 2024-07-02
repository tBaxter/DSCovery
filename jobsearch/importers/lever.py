from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup


root_url = 'https://jobs.lever.co'

# Name, GH key
firms = [
    ('Bixal', 'bixal'),
    ('Coforma', 'coforma'),
    ('Corbalt', 'corbalt'),
    ('Exygy', 'exygy'),
    ('Mastrics', 'mastrics'),
    ('MO Studio', 'MOstudio'),
    ('Nava', 'nava'),
    ('Skyward', 'skywarditsolutions'),
    ('Softrams', 'softrams'),
    ('Truss', 'trussworks')
]


def get_jobs():
    jobs = []
    for firm in firms:
        co_name, key = firm
        print("Importing", co_name)
        url = root_url + '/' + key

        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good response for ", co_name, r.status_code)
            pass 
        soup = BeautifulSoup(r.content, "html.parser")
        job_wrapper = soup.find('div', class_='postings-wrapper')
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



        