import datetime
from jobsearch.importers import greenhouse_embedded

def test_greenhouse_embedded_title_cleanup():
    jobs = greenhouse_embedded.get_jobs()
    for job in jobs:
        # Title should not contain tag/badge/feature words
        assert not any(word in job['title'].lower() for word in ['tag', 'badge', 'new', 'featured'])
        assert job['title']
        assert isinstance(job['pub_date'], datetime.date)
