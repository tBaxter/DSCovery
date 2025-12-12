from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

from jobsearch.importers.utils import already_in_jobs

root_url = 'https://boards.greenhouse.io'

# Name, GH key
firms = [
    ('540.co', '540'),
    ('A1M', 'a1msolutions'),
    ('Agile Six', 'agilesix'),
    ('Aquia', 'aquia'),
    ('Bloom Works', 'bloomworks'),
    ('CivicActions', 'civicactions'),
    ('Oddball', 'oddball'),
    ('Raft', 'raft'),
]

def get_jobs():
    jobs = []
    print("Importing greenhouse")
    for firm in firms:    
        co_name, key = firm
        url = root_url + '/' + key

        r = requests.get(url, headers=settings.IMPORTER_HEADERS)

        if r.status_code != 200:
            print("Failed to get good response for %s: %s " % (co_name, r.status_code))
            url = 'https://job-boards.greenhouse.io/' + '/' + key
            r = requests.get(url, headers=settings.IMPORTER_HEADERS)
            if r.status_code != 200:
                print("Failed to get good response with alt_url for %s: %s " % (co_name, r.status_code))
                pass 
        
        soup = BeautifulSoup(r.content, "html.parser")
        sections = soup.find_all('section', class_="level-0")
        # For some reason, sometimes Greenhouse outputs as a table
        # so we have to get sections differently.
        # Looking at you, A1M
        table_layout = False
        if len(sections) == 0:
            table_layout = True
        for section in sections:
            section_title =  section.find('h3').text.strip()
            job_cards = section.find_all('div', class_="opening")

            for card in job_cards:
                job_title = card.find("a").text.strip()
                title = f"{section_title}: {job_title}"
                link = root_url + card.find('a')['href']
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
        if table_layout: # do it again for the weird layout
            sections = soup.find_all('div', class_="job-posts")
            for section in sections:
                section_title =  section.find('h3').text.strip()
                job_cards = section.find_all('tr', class_="job-post")

                for card in job_cards:
                    job_title = card.find("p", class_="body--medium")
                    # quick cleanup to remove junk from within th title
                    for child in job_title.find_all("span"):
                        child.decompose()
                    job_title = job_title.text.strip()
                    title = f"{section_title}: {job_title}"
                    link = card.find('a')['href']
                    new_job = {
                        'company': co_name,
                        'job_id': link.rsplit('/')[-1],
                        'title': title,
                        'link': link,
                        'location': card.find('p', class_="body--metadata").text.strip(),
                        'pub_date': datetime.date.today()
                    }
                    if not already_in_jobs(new_job, jobs):
                        jobs.append(new_job)

    return jobs

 