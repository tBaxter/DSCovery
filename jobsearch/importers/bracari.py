from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

company = "Bracari"
root_url = 'https://www.bracari.com'
url = root_url + '/join-us'

def get_jobs():
    print("Importing", company)
    r = requests.get(url, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        #print("Failed to get good requests response: ", r.status_code)
        return 
    soup = BeautifulSoup(r.content, "html.parser")

    job_cards = soup.find_all('a', class_="career-card")
    jobs = []
    for card in job_cards:
        title =  card.find('div', class_="text-bold").text.strip()
        link = root_url + card['href']
        jobs.append({
            'company': company,
            'job_id': link.rsplit('/')[-1],
            'title': title,
            'link': link,
            'location': card.find('div', class_="text-gray-1").text.strip(),
            'pub_date': datetime.date.today()
        })    
    return jobs
 