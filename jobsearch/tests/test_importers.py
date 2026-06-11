import datetime
from jobsearch.importers import greenhouse, exygy, greenhouse_embedded


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
        assert job['job_type'] in [
            'design', 'engineering', 'product', 'data', 'content', 'other'
        ]


def test_greenhouse_embedded_title_cleanup():
    jobs = greenhouse_embedded.get_jobs()
    for job in jobs:
        assert not any(word in job['title'].lower() for word in ['tag', 'badge', 'new', 'featured'])
        assert job['title']
        assert isinstance(job['pub_date'], datetime.date)
