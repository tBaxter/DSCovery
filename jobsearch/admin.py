from django.contrib import admin

from jobsearch.models import Job, JobSearch


class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "location", "pub_date"]


class JobSearchAdmin(admin.ModelAdmin):
    pass


admin.site.register(Job, JobAdmin)
admin.site.register(JobSearch, JobSearchAdmin)
