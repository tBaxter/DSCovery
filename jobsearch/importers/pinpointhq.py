import requests
from django.conf import settings
import json
from datetime import datetime, timezone

from jobsearch.importers.utils import fetch_response

# Name, base URL
firms = [
    ('Coforma', 'https://coforma.pinpointhq.com'),
]

def get_jobs():
    jobs = []
    
    for firm in firms:
        co_name, base_url = firm
        # print(f"Importing {co_name}")
        
        try:
            jobs.extend(_scrape_jobs_json(base_url, co_name))
        except Exception as e:
            print(f"Failed to scrape {co_name}: {e}")
    
    return jobs

def _scrape_jobs_json(base_url, co_name):
    """Scrape jobs from Pinpointhq JSON API"""
    jobs = []
    
    try:
        # Fetch the postings JSON directly
        postings_url = f"{base_url}/en/postings"
        headers = settings.IMPORTER_HEADERS.copy() if hasattr(settings, 'IMPORTER_HEADERS') else {}
        
        response = fetch_response('get', postings_url, importer_name=co_name, headers=headers, timeout=30)
        if response is None:
            return jobs
        
        # Parse JSON data
        data = response.json()
        
        for job_data in data.get('data', []):
            try:
                # Skip general application postings
                title = job_data.get('title', '').strip()
                if 'general application' in title.lower():
                    continue
                
                # Extract job details
                job_id = job_data.get('id')
                url = job_data.get('url')
                location_data = job_data.get('location', {})
                if isinstance(location_data, dict):
                    location = location_data.get('name', 'Remote')
                else:
                    location = str(location_data) if location_data else 'Remote'
                
                # Parse compensation if available
                compensation = job_data.get('compensation')
                salary_info = None
                if compensation and job_data.get('compensation_visible', False):
                    if isinstance(compensation, dict):
                        min_salary = compensation.get('compensation_minimum')
                        max_salary = compensation.get('compensation_maximum')
                        currency = compensation.get('compensation_currency', 'USD')
                        frequency = compensation.get('compensation_frequency', 'year')
                        
                        if min_salary and max_salary:
                            salary_info = f"${min_salary:,.0f} - ${max_salary:,.0f} {currency} per {frequency}"
                        elif min_salary:
                            salary_info = f"${min_salary:,.0f} {currency} per {frequency}"
                    elif isinstance(compensation, str):
                        # Use the pre-formatted string
                        salary_info = compensation
                
                # Use current date as pub_date since API doesn't provide it
                pub_date = datetime.now(timezone.utc).date().isoformat()
                
                job = {
                    'company': co_name,
                    'title': title,
                    'link': url,
                    'location': location,
                    'job_id': str(job_id),
                    'pub_date': pub_date,
                }
                
                if salary_info:
                    job['salary'] = salary_info
                
                jobs.append(job)
                
            except Exception as e:
                print(f"Error parsing job data: {e}")
                continue
                
    except requests.RequestException as e:
        print(f"Request error for {co_name}: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON parse error for {co_name}: {e}")
    
    return jobs