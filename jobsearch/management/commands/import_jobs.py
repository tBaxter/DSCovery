from django.core.management.base import BaseCommand
from django.utils import timezone
from jobsearch.importers import get_all_jobs
from jobsearch.models import Job, Company, Profile
from datetime import datetime, date, time

class Command(BaseCommand):
    help = "Import jobs from ALL importers into the Job model"

    def handle(self, *args, **kwargs):
        default_user = Profile.objects.first()
        if not default_user:
            self.stdout.write(self.style.ERROR("No default user found."))
            return

        jobs = get_all_jobs()
        self.stdout.write(self.style.SUCCESS(f"Found {len(jobs)} scraped jobs"))

        new_count = 0
        update_count = 0

        for j in jobs:
            # Parse/convert pub_date
            pub_date = j.get('pub_date')
            if isinstance(pub_date, str):
                pub_date = datetime.fromisoformat(pub_date)
            if isinstance(pub_date, date) and not isinstance(pub_date, datetime):
                pub_date = datetime.combine(pub_date, time.min)
            if timezone.is_naive(pub_date):
                pub_date = timezone.make_aware(pub_date)

            company_obj, _ = Company.objects.get_or_create(importer_name=j['company'])
            obj, created = Job.objects.update_or_create(
                job_id=j['job_id'],
                defaults={
                    'title': j['title'],
                    'link': j['link'],
                    'location': j['location'],
                    'pub_date': pub_date,
                    'user': default_user,
                    'new_company': company_obj,
                }
            )
            if created:
                new_count += 1
            else:
                update_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Imported {new_count} new, updated {update_count} existing jobs."
        ))