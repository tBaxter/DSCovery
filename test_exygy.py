import datetime
from jobsearch.importers import exygy

def test_exygy_get_jobs():
    jobs = exygy.get_jobs()
    assert isinstance(jobs, list)
    for job in jobs:
        assert job['company'] == 'Exygy'
        assert job['title']
        assert job['link'].startswith('https://exygy.com/')
        assert job['job_id'].startswith('exygy-')
        assert job['location']
        assert isinstance(job['pub_date'], datetime.date)
        assert 'details' in job
        assert 'job_type' in job
        # Optionally, check job_type is in allowed choices
        assert job['job_type'] in [
            'design', 'engineering', 'product', 'data', 'content', 'other'
        ]
