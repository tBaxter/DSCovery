from django.contrib import admin

from django import forms
from django.utils.html import format_html
from django.contrib import admin

from jobsearch.models import Group, Company, Job, Agency


class AgencyAdmin(admin.ModelAdmin):
    pass


class GroupAdmin(admin.ModelAdmin):
    pass


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make co_link required in the admin form (no DB migration)
        if 'co_link' in self.fields:
            self.fields['co_link'].required = True


class CompanyAdmin(admin.ModelAdmin):
    form = CompanyForm
    list_display = ["importer_name", "link", "importer_type"]
    filter_horizontal = ("agencies",)

    def link(self, obj):
        # show the company link; prefer an anchor if it looks like a URL
        if obj.co_link:
            if obj.co_link.startswith('http'):
                return format_html('<a href="{}" target="_blank">{}</a>', obj.co_link, obj.co_link)
            return obj.co_link
        return ''
    link.short_description = 'link'


class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "new_company", "location", "pub_date", "job_type"]
    list_editable = ['job_type']
    list_filter = ["new_company"]


admin.site.register(Agency, AgencyAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Group, GroupAdmin)
