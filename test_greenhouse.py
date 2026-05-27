import datetime
from jobsearch.importers import greenhouse

def test_greenhouse_practice_mapping():
    jobs = greenhouse.get_jobs()
    for job in jobs:
        assert 'job_type' in job
        assert job['job_type'] in [
            'office', 'bd', 'content', 'data', 'delivery', 'design', 'engineering',
            'help', 'product', 'security', 'other'
        ]
        assert job['title']
        assert isinstance(job['pub_date'], datetime.date)
