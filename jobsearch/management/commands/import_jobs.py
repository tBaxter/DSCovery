from django.core.management.base import BaseCommand
from jobsearch.importers import paylocity
from jobsearch.models import Job, Company, Profile


class Command(BaseCommand):
    help = "Import jobs from Paylocity into the Job model"

    def handle(self, *args, **kwargs):
        default_user = Profile.objects.first()
        if not default_user:
            self.stdout.write(self.style.ERROR("❌ No default user found. Please create a user first."))
            return

        jobs = paylocity.get_jobs()
        self.stdout.write(self.style.SUCCESS(f"🔍 Found {len(jobs)} scraped jobs"))

        created_count = 0
        for j in jobs:
            company_obj, _ = Company.objects.get_or_create(importer_name=j['company'])
            _, created = Job.objects.update_or_create(
                job_id=j['job_id'],
                defaults={
                    'title': j['title'],
                    'link': j['link'],
                    'location': j['location'],
                    'pub_date': j['pub_date'],
                    'user': default_user,
                    'new_company': company_obj,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Imported {created_count} new jobs."))