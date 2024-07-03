from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

root_url = '.applytojob.com/apply/'

# Name, key
firms = [
    ('Analytica', 'analyticallc'),
    ('Mobomo', 'mobomo'),
]


def get_jobs():
    jobs = []
    for firm in firms:    
        co_name, key = firm
        print("Importing", co_name)
        url = 'https://' + key + root_url
        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good requests response: ", r.status_code)
            return 
        soup = BeautifulSoup(r.content, "html.parser")
        job_cards = soup.find('div', class_='jobs-list').find_all('li', class_="list-group-item")
        jobs = []
        for card in job_cards:
            title =  card.find('h4', class_="list-group-item-heading")
            link = title.find('a')['href']
            jobs.append({
                'company': co_name,
                'title': title.text.strip(),
                'link': link,
                'job_id': link.rsplit('/')[-2],
                'location': card.find('ul', class_="list-inline").text.strip(),
                'pub_date': datetime.date.today()
            })
    return jobs


        