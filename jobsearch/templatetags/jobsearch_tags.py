
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

    from datetime import datetime, timedelta
    import pytz
    now = datetime.now(pytz.utc)
    week_ago = now - timedelta(days=7)
    jobs = company.job_set.filter(rejected=False)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    jobs = jobs.order_by('-pub_date')
    # Annotate jobs with is_new
    for job in jobs:
        job.is_new = job.pub_date and job.pub_date >= week_ago
    return {
        'jobs': jobs,
        'job_type': job_type,
        'company': company
    }
