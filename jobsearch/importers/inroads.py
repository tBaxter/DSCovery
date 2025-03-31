import datetime
import requests
from bs4 import BeautifulSoup
from django.conf import settings

url = 'https://boards.greenhouse.io/embed/job_board/js?for=inroads'

def get_jobs():
    print("Importing Inroads")
    r = requests.get(url, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        print("Failed to get response:", r.status_code)
        return

    # NOTE: Greenhouse embeds their job content via JS, so we can't scrape jobs from this script URL.
    # We'll instead hit the actual job board in HTML form:
    html_url = "https://boards.greenhouse.io/inroads"
    r = requests.get(html_url, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        print("Failed to get response:", r.status_code)
        return

    soup = BeautifulSoup(r.content, "html.parser")
    jobs = []
    job_cards = soup.find_all("div", class_="opening")
    
    for card in job_cards:
        title_tag = card.find("a")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = "https://boards.greenhouse.io" + title_tag["href"]
        location = card.find_next_sibling("span", class_="location").text.strip() if card.find_next_sibling("span", class_="location") else "Remote"
        jobs.append({
            'company': 'Inroads',
            'title': title,
            'link': link,
            'location': location,
            'job_id': link.rsplit("/", 1)[-1],
            'pub_date': datetime.date.today()
        })
    
    return jobs
