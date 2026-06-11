

import requests


def fetch_response(method, url, importer_name=None, **kwargs):
    """Execute a requests call and log non-200 or failed responses."""
    target = importer_name if importer_name else url
    try:
        response = getattr(requests, method)(url, **kwargs)
    except Exception as e:
        print(f"Request failed for {target}: {e}")
        return None

    if response.status_code != 200:
        print(f"Non-200 response for {target}: {response.status_code} {url}")
        return None

    return response


def already_in_jobs(new_job, jobs):
    """
    Simple helper function to check if a similar-ish item is already in the list of jobs
    based on the company and job name.
    """
    return any(
        job['company'] == new_job['company'] and job['title'] == new_job['title']
        for job in jobs
    )

def map_section_to_practice(section_title):
    section_lower = section_title.lower()
    mappings = {
        'engineering': 'engineering',
        'developer': 'engineering',
        'backend': 'engineering',
        'frontend': 'engineering',
        'design': 'design',
        'ux': 'design',
        'research': 'design',
        'product': 'product',
        'pm': 'product',
        'data': 'data',
        'analytics': 'data',
        'business development': 'bd',
        'sales': 'bd',
        'marketing': 'content',
        'content': 'content',
        'communications': 'content',
        'security': 'security',
        'devops': 'engineering',
        'infra': 'engineering',
        'operations': 'office',
        'finance': 'office',
        'human resources': 'office',
        'hr': 'office',
        'support': 'help',
        'customer success': 'help',
        'cs': 'help',
    }
    for keyword, practice in mappings.items():
        if keyword in section_lower:
            return practice
    return 'other'
