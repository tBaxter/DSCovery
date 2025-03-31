import datetime
import requests
from bs4 import BeautifulSoup

from django.conf import settings

url = 'https://mediabarnstaffing.com/jobs/'

def get_jobs():
    print("Importing Mediabarn")
    r = requests.get(url, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        print("Failed to get response:", r.status_code)
        return

    soup = BeautifulSoup(r.content, "html.parser")
    jobs = []

    job_cards = soup.find_all("div", class_="job-listing")
    for card in job_cards:
        link_tag = card.find("a", href=True)
        if not link_tag:
            continue

        title = link_tag.text.strip()
        link = link_tag["href"]
        location = card.find("span", class_="job-location").text.strip() if card.find("span", class_="job-location") else "Remote"

        jobs.append({
            'company': 'Mediabarn',
            'title': title,
            'link': link,
            'location': location,
            'job_id': link.rsplit("/", 1)[-1],
            'pub_date': datetime.date.today()
        })

    return jobs
