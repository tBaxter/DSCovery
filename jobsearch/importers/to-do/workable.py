from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup


# Name, key
firms = [
    ('Blue Tiger', 'https://www.bluetiger.digital/careers'),
    #('Friends from the City', 'friends-from-the-city'),
    #('Pixel Creative', 'pixelcreative'),
]


def get_jobs():
    print("attempting to import workable")
    jobs = []
    for firm in firms:    
        co_name, key = firm
        url = key
        print("importing from ", url)
        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good response for ", co_name, r.status_code)
            pass 
        soup = BeautifulSoup(r.content, "html.parser")
        content = soup.find('div', class_='sqs-html-content')
        job_cards = content.find_all('a')
        for card in job_cards:
            title = card.text.strip()
            link = card['href']
            jobs.append({
                'company': co_name,
                'job_id': link.rsplit('/')[-1],
                'title': title,
                'link': link,
                'location': '',
                'pub_date': datetime.date.today()
            })
        print(jobs)
    return jobs
 