from django.contrib import admin

from jobsearch.models import Group, Company, Job, Agency


class AgencyAdmin(admin.ModelAdmin):
    pass

class GroupAdmin(admin.ModelAdmin):
    pass

class CompanyAdmin(admin.ModelAdmin):
    pass

class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "new_company", "location", "pub_date"]
    list_filter = ["new_company"]



admin.site.register(Agency, AgencyAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Group, GroupAdmin)
