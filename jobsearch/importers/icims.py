from django.conf import settings
import datetime
import requests
import re
from bs4 import BeautifulSoup

from jobsearch.importers.utils import already_in_jobs

# Name, career board URL
firms = [
    ('Valiant', 'https://careers-valiantsolutions.icims.com/jobs/search?hashed=-435594529&mobile=false&width=565&height=500&bga=true&needsRedirect=false&jan1offset=-300&jun1offset=-240'),
    ('Steampunk', 'https://careers-steampunk.icims.com/jobs/search?ss=1&hashed=-435593565'),
    ('Granicus', 'https://careers-granicus.icims.com/jobs/search'),
]

def get_jobs():
    jobs = []
    
    for company_name, url in firms:
        # print("Importing", company_name)
        
        # Append in_iframe=1 to get the job listing (served in embedded iframe)
        url = url + '&in_iframe=1'
        
        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good response for %s: %s" % (company_name, r.status_code))
            pass
        
        soup = BeautifulSoup(r.content, "html.parser")
        job_cards = soup.find_all('li', class_='iCIMS_JobCardItem')
        
        for card in job_cards:
            # Extract job title from the anchor tag
            title_elem = card.find('a')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True).replace('Job Title', '').strip()
            link = title_elem.get('href', '')
            
            if not title or not link:
                continue
            
            # Extract job_id from the URL
            job_id_match = re.search(r'/jobs/(\d+)/', link)
            job_id = job_id_match.group(1) if job_id_match else link.rsplit('/')[-1]
            
            # Extract location
            location_elem = card.find('span', string=re.compile('Job Location'))
            location = 'Unknown'
            if location_elem:
                loc_span = location_elem.find_next('span')
                if loc_span:
                    location = loc_span.get_text(strip=True)
            
            # Extract posted date
            pub_date = datetime.date.today()
            posted_elem = card.find('span', string=re.compile('Posted Date'))
            if posted_elem:
                date_span = posted_elem.find_next('span')
                if date_span:
                    date_str = date_span.get('title', '')
                    if date_str:
                        try:
                            pub_date = datetime.datetime.strptime(date_str, '%m/%d/%Y %I:%M %p').date()
                        except:
                            pass
            
            new_job = {
                'company': company_name,
                'job_id': job_id,
                'title': title,
                'link': link,
                'location': location,
                'pub_date': pub_date
            }
            
            if not already_in_jobs(new_job, jobs):
                jobs.append(new_job)
    
    return jobs