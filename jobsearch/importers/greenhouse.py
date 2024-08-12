from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup


root_url = 'https://boards.greenhouse.io'

# Name, GH key
firms = [
    ('540', '540'),
    ('Agile Six', 'agilesix'),
    ('Bloom Works', 'bloomworks'),
    ('CivicActions', 'civicactions'),
    ('Oddball', 'oddball'),
    ('Raft', 'raft'),
]

def get_jobs():
    jobs = []
    for firm in firms:    
        co_name, key = firm
        print("Importing", co_name)
        url = root_url + '/' + key

        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            #print("Failed to get good requests response: ", r.status_code)
            pass 
        
        soup = BeautifulSoup(r.content, "html.parser")
        sections = soup.find_all('section', class_="level-0")
        for section in sections:
            section_title =  section.find('h3').text.strip()
            job_cards = section.find_all('div', class_="opening")

            for card in job_cards:
                job_title = card.find("a").text.strip()
                title = f"{section_title}: {job_title}"
                link = root_url + card.find('a')['href']
                jobs.append({
                    'company': co_name,
                    'job_id': link.rsplit('/')[-1],
                    'title': title,
                    'link': link,
                    'location': card.find('span', class_="location").text.strip(),
                    'pub_date': datetime.date.today()
                })
    return jobs
 