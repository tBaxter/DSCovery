import datetime
import requests
from bs4 import BeautifulSoup

from django.conf import settings

url = 'https://recruiting.paylocity.com/recruiting/jobs/All/7d5de2cb-45b0-4c7b-a9bb-79a35a938e08/Snowbird-Agility'

def get_jobs():
    print("Importing Snowbird Agility")
    r = requests.get(url, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        print("Failed to get response:", r.status_code)
        return

    soup = BeautifulSoup(r.content, "html.parser")
    job_cards = soup.find_all("div", class_="card-body")
    jobs = []

    for card in job_cards:
        title_tag = card.find("h5")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        link = card.find("a", href=True)
        full_link = url if not link else url + link["href"]
        location = card.find("div", class_="location").text.strip() if card.find("div", class_="location") else "Remote"

        jobs.append({
            'company': 'Snowbird Agility',
            'title': title,
            'link': full_link,
            'location': location,
            'job_id': full_link.rsplit("/", 1)[-1],
            'pub_date': datetime.date.today()
        })

    return jobs
