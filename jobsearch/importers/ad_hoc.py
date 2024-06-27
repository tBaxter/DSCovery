import datetime
import requests
from bs4 import BeautifulSoup

from django.conf import settings
from django.utils.timezone import make_aware


# UKG -- Ad Hoc's HR system -- is such an inmitigated pile of dog vomit we have little choice but 
# to get the results from linkedin. It's just terrible, and the fool who chose the system should be embarrassed.

url = 'https://www.linkedin.com/jobs/search/?f_C=10350118&keywords=ad%20hoc%20llc&origin=JOB_SEARCH_PAGE_JOB_FILTER'

def get_jobs():
    print("Importing Ad Hoc from Linkedin")
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
            'job_id': card['data-entity-urn'].rsplit(':')[-1],
            'link': card.find('a', class_="base-card__full-link")['href'],
            'location': card.find('span', class_='job-search-card__location').text.strip(),
            'pub_date': card.find('time')['datetime']
        })
        
    return jobs
        