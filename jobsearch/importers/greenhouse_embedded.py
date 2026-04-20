from django.conf import settings
import datetime
import requests
from bs4 import BeautifulSoup

from jobsearch.importers.utils import already_in_jobs

root_url = 'https://boards.greenhouse.io/embed/job_board?for='
alternate_url = 'https://job-boards.greenhouse.io/embed/job_board?for='

# Name, GH key
firms = [
    ('BlueLabs', 'bluelabsanalyticsinc'),
    ('Capital Technology Group', 'capitaltg'),
    # ('MetroStar', 'metrostarsystems'), Metrostar floods the site. Don't know how to fix.
    ('PBG Consulting', 'pbgconsultingllc'),
    ('Pluribus Digital', 'pluribusdigital'),
    ('[Simple]', 'simpletechnologysolutions'),
    ('Skylight', 'skylighthq'),
    ('Softrams', "triafederal"),
    ('Inroads', 'inroads'),
    ('Truss', 'trussworksinc'),
]




def get_jobs():
    jobs = []
    for firm in firms:    
        co_name, key = firm
        # print("Importing", co_name)
        url = root_url + key
        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good response for ", co_name, r.status_code)
            print ("Trying alternate url for ", co_name)
            url = alternate_url + key
            r = requests.get(url, headers=settings.IMPORTER_HEADERS)
            if r.status_code != 200:
                print("Failed to get good response with alt_url for %s: %s " % (co_name, r.status_code))    
                continue 
    
        soup = BeautifulSoup(r.content, "html.parser")
        sections = soup.find_all('section', class_="level-0")
        print(f"Found {len(sections)} sections for {co_name}")
        
        for section in sections:
            try:
                section_title =  section.find('h3').text.strip()
            except:
                # but some people put it in an H2, and if we can't find one at all, we still need a value.
                h2_tag = section.find('h2')
                section_title = h2_tag.text.strip() if h2_tag else '' 
            # now get the cards for that section
            job_cards = section.find_all('div', class_="opening")
            print(f"Found {len(job_cards)} job cards in section '{section_title}' for {co_name}")
            
            for card in job_cards:
                try:
                    a_tag = card.find("a")
                    if not a_tag:
                        continue
                    job_title = a_tag.text.strip()
                    title = f"{section_title}: {job_title}" if section_title else job_title
                    link = a_tag.get('href', '')
                    if not link:
                        continue
                    
                    location_span = card.find('span', class_="location")
                    location = location_span.text.strip() if location_span else 'Unknown'
                    
                    new_job = {
                        'company': co_name,
                        'job_id': link.rsplit('/')[-1],
                        'title': title,
                        'link': link,
                        'location': location,
                        'pub_date': datetime.date.today()
                    }
                    if not already_in_jobs(new_job, jobs):
                        jobs.append(new_job)
                    else:
                        print("Job already exists for %s and %s." % (co_name, title))
                except Exception as e:
                    print(f"Error parsing job card for {co_name}: {e}") 
    return jobs
 