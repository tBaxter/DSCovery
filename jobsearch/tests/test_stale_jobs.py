from django.contrib.auth import get_user_model
from django.test import TestCase

from jobsearch.models import Company, Job
from jobsearch.views import delete_stale_jobs


class DeleteStaleJobsTests(TestCase):
    def test_delete_stale_jobs_removes_missing_jobs_only(self):
        User = get_user_model()
        user = User.objects.create_user(username='tester', password='secret')
        company = Company.objects.create(importer_name='Acme')

        still_current = Job.objects.create(
            title='Senior Engineer',
            new_company=company,
            location='Remote',
            link='https://example.com/jobs/current',
            pub_date='2026-01-01T00:00:00Z',
            job_id='current-job',
            user=user,
        )
        stale = Job.objects.create(
            title='Old Position',
            new_company=company,
            location='Remote',
            link='https://example.com/jobs/stale',
            pub_date='2026-01-01T00:00:00Z',
            job_id='stale-job',
            user=user,
        )

        imported_jobs = [
            {
                'company': 'Acme',
                'title': 'Senior Engineer',
                'link': 'https://example.com/jobs/current',
                'location': 'Remote',
                'pub_date': '2026-01-01T00:00:00Z',
                'job_id': 'current-job',
            }
        ]

        delete_stale_jobs(user, imported_jobs)

        self.assertTrue(Job.objects.filter(pk=still_current.pk).exists())
        self.assertFalse(Job.objects.filter(pk=stale.pk).exists())
