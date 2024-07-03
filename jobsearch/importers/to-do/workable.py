from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

# sample job: https://apply.workable.com/friends-from-the-city/j/98BEF80094/

#Pixel: Uses workable. No jobs open. https://apply.workable.com/pixelcreative/


# Can't figure out how workable is hydrated. I'll have to pull the listings from Linkedin or else use Selenium.

root_url = 'https://apply.workable.com'

# Name, key
firms = [
    ('Friends from the City', 'friends-from-the-city'),
    ('Pixel Creative', 'pixelcreative'),
]


def get_jobs():
    jobs = []
    for firm in firms:    
        co_name, key = firm
        print("Importing", co_name)
        url = root_url + '/' + key

        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good response for ", co_name, r.status_code)
            pass 
        soup = BeautifulSoup(r.content, "html.parser")
        job_cards = soup.find_all(attrs={"data-ui": "job"})
        elements = soup.find_all(attrs={"data-ui": "job"})
        print(job_cards)
        for card in job_cards:
            title = card.find('h3').text.strip()
            link = root_url + card.find('a')['href']
            jobs.append({
                'company': co_name,
                'job_id': link.rsplit('/')[-1],
                'title': title,
                'link': link,
                'location': card.find(attrs={"data-ui": "job-workplace"}).text.strip(),
                'pub_date': datetime.date.today()
            })
        print(jobs)
    return jobs
 