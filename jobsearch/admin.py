from django.contrib import admin

from jobsearch.models import Company, Job, JobSearch


class CompanyAdmin(admin.ModelAdmin):
    pass


class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "new_company", "location", "pub_date"]
    list_filter = ["new_company"]


class JobSearchAdmin(admin.ModelAdmin):
    pass

admin.site.register(Company, CompanyAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(JobSearch, JobSearchAdmin)
