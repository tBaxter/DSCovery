
from django import template

register = template.Library()


@register.inclusion_tag('includes/job_list_body.html', takes_context=True)
def show_jobs(context, company, job_type):
    """
    Creates job list for a given company, 
    filtered as needed for job type
    and/or user preferences.
    """
    output_text = u''

    jobs = company.job_set.filter(rejected=False).order_by("job_type", "title")
    if job_type:
        jobs = jobs.filter(rejected=False, job_type=job_type).order_by("title")

    return {
        'jobs': jobs,
        'job_type': job_type,
        'company': company
    }
