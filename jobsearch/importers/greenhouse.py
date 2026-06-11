from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

from jobsearch.importers.utils import already_in_jobs, fetch_response, map_section_to_practice

root_url = 'https://boards.greenhouse.io'

# Name, GH key
firms = [
    # ('540.co', '540'), removed because of focus of work
    ('A1M', 'a1msolutions'),
    ('Agile Six', 'agilesix'),
    ('Aquia', 'aquia'),
    ('Bloom Works', 'bloomworks'),
    ('CivicActions', 'civicactions'),
    ('Nava', 'navapbc'),
    ('Oddball', 'oddball'),
    ('Raft', 'raft'),
]

def get_jobs():
    jobs = []
    # print("Importing greenhouse")
    for firm in firms:    
        co_name, key = firm
        url = root_url + '/' + key

        r = fetch_response('get', url, importer_name=co_name, headers=settings.IMPORTER_HEADERS)

        if not r:
            url = 'https://job-boards.greenhouse.io/' + '/' + key
            r = fetch_response('get', url, importer_name=co_name, headers=settings.IMPORTER_HEADERS)
            if not r:
                continue
        
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
            job_type = map_section_to_practice(section_title)
            job_cards = section.find_all('div', class_="opening")

            for card in job_cards:
                a_tag = card.find("a")
                if a_tag:
                    # Remove extraneous child elements (like 'new', 'tag', etc.)
                    for child in a_tag.find_all(['span', 'badge', 'em', 'strong']):
                        if any(cls in child.get('class', []) for cls in ['tag', 'badge', 'new', 'featured']):
                            child.decompose()
                    job_title = a_tag.get_text(strip=True)
                else:
                    job_title = ''
                title = f"{job_title}"
                link = root_url + a_tag['href'] if a_tag else ''
                new_job = {
                    'company': co_name,
                    'job_id': link.rsplit('/')[-1],
                    'title': title,
                    'link': link,
                    'location': card.find('span', class_="location").text.strip(),
                    'pub_date': datetime.date.today(),
                    'job_type': job_type
                }
                if not already_in_jobs(new_job, jobs):
                    jobs.append(new_job)
        if table_layout: # do it again for the weird layout
            sections = soup.find_all('div', class_="job-posts")
            for section in sections:
                section_title =  section.find('h3').text.strip()
                job_type = map_section_to_practice(section_title)
                job_cards = section.find_all('tr', class_="job-post")

                for card in job_cards:
                    job_title = card.find("p", class_="body--medium")
                    # quick cleanup to remove junk from within th title
                    for child in job_title.find_all("span"):
                        child.decompose()
                    job_title = job_title.text.strip()
                    title = f"{job_title}"
                    link = card.find('a')['href']
                    new_job = {
                        'company': co_name,
                        'job_id': link.rsplit('/')[-1],
                        'title': title,
                        'link': link,
                        'location': card.find('p', class_="body--metadata").text.strip(),
                        'pub_date': datetime.date.today(),
                        'job_type': job_type
                    }
                    if not already_in_jobs(new_job, jobs):
                        jobs.append(new_job)

    return jobs

 