from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

company = "Kind"

url = "https://kindsystems.notion.site/Kind-Jobs-a9a393359d88400c9c8912f8d1436658"

"""
Uses notion? and I want to see at least one other company with it before I deal with it. 
Also no current openings as of 6/26
"""

def get_jobs():
    """
    TO-DO: Come back to this
    """
    return
    r = requests.get(url, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        #print("Failed to get good requests response: ", r.status_code)
        return 
    soup = BeautifulSoup(r.content, "html.parser")
    job_cards = soup.find_all('section', class_="level-0")
    jobs = []
    for card in job_cards:
        section_title =  card.find('h3').text.strip()
        job_title = card.find('div', class_="opening").find("a").text.strip()
        title = f"{section_title}: {job_title}"
        link = card.find('a')['href']
        jobs.append({
            'company': company,
            'job_id': link.rsplit('/')[-1],
            'title': title,
            'link': link,
            'location': card.find('span', class_="location").text.strip(),
            'pub_date': datetime.date.today()
        })    
    return jobs
 