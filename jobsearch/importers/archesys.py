from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

url = 'https://www.archesys.io/roles'

def get_jobs():
    print("Importing ArcheSys")
    r = requests.get(url, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        print("Failed to get good requests response: ", r.status_code)
        return 
    soup = BeautifulSoup(r.content, "html.parser")
    job_cards = soup.find('div', class_='job_wrapper').find_all('div', class_="job_list")
    jobs = []
    for card in job_cards:
        link = url + card.find('a')['href'].replace('/roles', '')
        title = card.find("a").text.strip()
        location = card.find('div', class_="text-size-small").text.strip()
        jobs.append({
            'company': 'ArcheSys',
            'title': title,
            'link': link,
            'location': location,
            'job_id': link.rsplit('/')[-1],
            'pub_date': datetime.date.today()
        })
    return jobs



        