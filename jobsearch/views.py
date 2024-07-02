import os
import requests
import importlib.util

from bs4 import BeautifulSoup

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .forms import JobStatusForm
from .models import Job, Company


class JobListView(ListView):
    model = Job
    context_object_name = "jobs"

    def get_queryset(self):
        return Job.objects.filter(rejected=False).order_by('company')
    
    def get_context_data(self, **kwargs):
        context = super(JobListView, self).get_context_data(**kwargs)
        context['jobs_list'] = {}
        for item in context['jobs']:
            company = item.company
            form = JobStatusForm(instance=item)
            # Check if the category key exists in grouped_dict
            if company in context['jobs_list']:
                context['jobs_list'][company].append((item, form))
            else:
                context['jobs_list'][company] = [(item, form)]
            
        return context

class JobDetailView(DetailView):
    model = Job

    def get_context_data(self, **kwargs):
        context = super(JobDetailView, self).get_context_data(**kwargs)
        
        return context


@login_required
def import_jobs(request):
    """
    Search for jobs matching our parameters.
    """
    user = request.user
    importers_dir = os.path.join(os.path.dirname(__file__), 'importers')
    jobs = []
    for file_name in os.listdir(importers_dir):
        if file_name.endswith('.py') and file_name != '__init__.py':
            module_name = file_name[:-3]  # Remove the .py extension
            module_path = os.path.join(importers_dir, file_name)
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            co_jobs = module.get_jobs()
            jobs.extend(co_jobs) if co_jobs is not None else jobs
    
    for job in jobs:
        try:
            Job.objects.get(job_id=job['job_id'], company=job['company'])
        except:
            try:
                print("importing ", job['company'], job['title'])
                company, created = Company.objects.get_or_create(importer_name=job['company'])
                newjob = Job (
                    title = job['title'],
                    link = job['link'],
                    company = job['company'],
                    new_company = company,
                    location = job['location'],
                    pub_date = job['pub_date'],
                    job_id = job['job_id'],
                    user=user
                )
                newjob.save()
            except Exception as e:
                print("failed to import", job, e)
                print("job:", job['title'], job['link'], job['company'], job['company'], job['location'],  job['pub_date'], job['job_id'])
    return HttpResponseRedirect(reverse('jobs'))


@login_required
def fetch_job_details(request):
    job = get_object_or_404(Job, pk=request.GET['pk'])
    r = requests.get(job.link, headers=settings.IMPORTER_HEADERS)
    if r.status_code != 200:
        return HttpResponse("Failed to get good requests response: ", r.status_code)
    soup = BeautifulSoup(r.content, "html.parser")
    desc = soup.find('div', class_="description__text")
    details = soup.find('div', class_="description__text").find("div", class_="show-more-less-html__markup").text.strip()
    job.details = details
    job.save()
    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        print("it's ajax")
        return render(request, 'includes/job_detail_td.html')
    return HttpResponseRedirect(reverse('jobs'))


@login_required
def reject_job(request):
    """ Deprecated. Moved to update job status below."""
    if request.POST:  
        job = get_object_or_404(Job, user=request.user, pk=request.POST['id'])
        job.rejected=True
        job.save()
    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return render(request, 'includes/job_detail_row.html')

    return HttpResponseRedirect(reverse('jobs'))

@login_required
def update_job_status(request):
    if request.POST:  
        job = get_object_or_404(Job, user=request.user, pk=request.POST['id'])
        if request.POST['status'] == "0": # rejected
            job.rejected=True
            job.save()
        f = JobStatusForm(request.POST, instance=job)
        f.save()
    return HttpResponseRedirect(reverse('jobs'))