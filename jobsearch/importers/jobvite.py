from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup
from jobsearch.importers.utils import fetch_response


root_url = 'https://jobs.jobvite.com'

# Name, GH key
firms = [
    ('Clarity Innovations', 'clarityinnovations'),
    ('ArcAspicio', 'arc-aspicio')
]

def get_jobs():
    jobs = []
    for firm in firms:
        co_name, key = firm
        # print("Importing", co_name)
        url = root_url + '/' + key

        r = fetch_response('get', url, importer_name=co_name, headers=settings.IMPORTER_HEADERS)
        if not r:
            continue
        
        soup = BeautifulSoup(r.content, "html.parser")
        job_tables = soup.find_all('table', class_="jv-job-list")
        for table in job_tables:
            job_cards = table.find_all('tr')

            for card in job_cards:
                title = card.find("td", class_="jv-job-list-name")
                location = card.find("td", class_="jv-job-list-location")
                if title and location: # only bother if we found both, and avoid some jobvite shenanigans
                    link = root_url + card.find('a')['href']
                    jobs.append({
                        'company': co_name,
                        'job_id': link.rsplit('/')[-1],
                        'title': title.text.strip(),
                        'link': link,
                        'location': location.text.strip(),
                        'pub_date': datetime.date.today()
                    })
    return jobs
 