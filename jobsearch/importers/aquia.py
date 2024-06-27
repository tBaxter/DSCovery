import datetime
import requests
from bs4 import BeautifulSoup

from django.conf import settings
from django.utils.timezone import make_aware


# Aquia doesn't have a jobs page. They just use linkedin.
# I'll need to double-check this works when they've got jobs.

url = 'https://www.linkedin.com/company/aquiainc/jobs/'

def get_jobs():
    print("Importing Aquia from Linkedin")
    r = requests.get(url, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        print("Failed to get good requests response: ", r.status_code)
        return 
    soup = BeautifulSoup(r.content, "html.parser")

    jobs = []
    for card in soup.find_all('div', class_="job-search-card"):        
        jobs.append({
            'company': card.find('h4', class_='base-search-card__subtitle').text.strip(),
            'title': card.find('h3', class_='base-search-card__title').text.strip(),
            'link': card.find('a', class_="base-card__full-link")['href'],
            'job_id': card['data-entity-urn'].rsplit(':')[-1],
            'location': card.find('span', class_='job-search-card__location').text.strip(),
            'pub_date': card.find('time')['datetime']
        })
    return jobs
        