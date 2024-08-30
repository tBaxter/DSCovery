from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

root_url = 'https://boards.greenhouse.io/embed/job_board?for='

# Name, GH key
firms = [
    ('BlueLabs', 'bluelabsanalyticsinc'),
    ('Capital Technology Group', 'capitaltg'),
    ('Fearless', 'fearless'),
    ('MetroStar', 'metrostarsystems'),
    ('PBG Consulting', 'pbgconsultingllc'),
    ('Pluribus Digital', 'pluribusdigital'),
    ('[Simple]', 'simpletechnologysolutions'),
    ('Skylight', 'skylighthq')
]

def get_jobs():
    jobs = []
    for firm in firms:    
        co_name, key = firm
        print("Importing", co_name)
        url = root_url + key
        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good response for ", co_name, r.status_code)
            pass 
    
        soup = BeautifulSoup(r.content, "html.parser")
        job_cards = soup.find_all('section', class_="level-0")
        for card in job_cards:
            section_title =  card.find('h3') # this is normal
            if not section_title:
                section_title= card.find('h2') # but some people do this (fearless)
            job_title = card.find('div', class_="opening").find("a").text.strip()
            try:
                title = f"{section_title.text.strip()}: {job_title}"
            except Exception:
                title = job_title
            link = card.find('a')['href']
            jobs.append({
                'company': co_name,
                'job_id': link.rsplit('/')[-1],
                'title': title,
                'link': link,
                'location': card.find('span', class_="location").text.strip(),
                'pub_date': datetime.date.today()
            })    
    return jobs
 