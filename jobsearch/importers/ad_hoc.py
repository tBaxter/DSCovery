import pytz
import requests
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta

from django.conf import settings

from jobsearch.importers.utils import already_in_jobs


# UKG -- Ad Hoc's HR system -- now has a direct RSS feed, so we can import directly
# instead of scraping LinkedIn.

url = 'https://adhoc.hrmdirect.com/employment/rss.php?search=true&cust_sort1=245588&'

def get_jobs():
    print("Importing Ad Hoc from RSS feed")
    
    try:
        r = requests.get(url, headers=settings.IMPORTER_HEADERS)
        if r.status_code != 200:
            print("Failed to get good requests response: ", r.status_code)
            return []
        
        root = ET.fromstring(r.content)
        items = root.findall('.//item')
        jobs = []
        
        for item in items:
            try:
                title = item.find('title').text
                link = item.find('link').text
                description = item.find('description').text
                pubdate_str = item.find('pubDate').text
                
                if pubdate_str:
                    pubdate_str = pubdate_str.strip().strip('"\'“”')
                
                if not all([title, link, pubdate_str]):
                    print(f"Skipping item missing required fields: title={bool(title)}, link={bool(link)}, pubdate={bool(pubdate_str)}")
                    continue
                
                # Parse pubDate into a timezone-aware datetime
                pub_date = datetime.strptime(pubdate_str, '%a, %d %b %Y %H:%M:%S %z')
                pub_date_utc = pub_date.astimezone(pytz.utc)
                
                # Filter for jobs from the last week
                one_week_ago = datetime.now(pytz.utc) - timedelta(days=7)
                if pub_date_utc >= one_week_ago:
                    # Extract job_id from link URL (req parameter)
                    job_id = link.split('req=')[-1] if 'req=' in link else link
                    
                    new_job = {
                        'company': 'Ad Hoc',
                        'title': title,
                        'job_id': job_id,
                        'link': link,
                        'location': 'Remote',  # Most jobs appear to be remote based on titles
                        'pub_date': pub_date_utc
                    }
                    
                    if not already_in_jobs(new_job, jobs):
                        jobs.append(new_job)
            except Exception as e:
                print(f"Error processing item: {e}")
                continue
        
        return jobs
    except Exception as e:
        print(f"Error in get_jobs: {e}")
        return []
        