from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

from jobsearch.importers.utils import already_in_jobs

root_url = 'https://boards.greenhouse.io/embed/job_board?for='

# Name, GH key
firms = [
    ('BlueLabs', 'bluelabsanalyticsinc'),
    ('Capital Technology Group', 'capitaltg'),
    ('Fearless', 'fearless'),
    #('MetroStar', 'metrostarsystems'),
    ('PBG Consulting', 'pbgconsultingllc'),
    ('Pluribus Digital', 'pluribusdigital'),
    ('[Simple]', 'simpletechnologysolutions'),
    ('Skylight', 'skylighthq'),
    ('Inroads', 'inroads')
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
        sections = soup.find_all('section', class_="level-0")
        for section in sections:
            try:
                section_title =  section.find('h3').text.strip()
            except:
                # but some people put it in an H2, and if we can't find one at all, we still need a value.
                section_title = section.find('h2').text if len(section.find('h2'))!=0 else '' 
            # now get the cards for that section
            job_cards = section.find_all('div', class_="opening")
            for card in job_cards:
                job_title = card.find("a").text.strip()
                try:
                    title = f"{section_title.text.strip()}: {job_title}"
                except Exception:
                    title = job_title
                link = card.find('a')['href']
                new_job = {
                    'company': co_name,
                    'job_id': link.rsplit('/')[-1],
                    'title': title,
                    'link': link,
                    'location': card.find('span', class_="location").text.strip(),
                    'pub_date': datetime.date.today()
                }
                if not already_in_jobs(new_job, jobs):
                    jobs.append(new_job)
                else:
                    print("Job already exists for %s and %s." % (co_name, title)) 
    return jobs
 