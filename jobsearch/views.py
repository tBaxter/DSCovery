import os
import pytz
import requests
import importlib.util
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .forms import JobStatusForm
from .models import Job, Company, PRACTICE_CHOICES


class JobListView(ListView):
    model = Company
    context_object_name = "companies"
    template_name = "jobsearch/job_list.html"

    """def get_queryset(self):
        #return Job.objects.filter(rejected=False).order_by('new_company')
        return Company.objects.all()
    """
    
    def get_context_data(self, **kwargs):
        context = super(JobListView, self).get_context_data(**kwargs)
        fresh = datetime.now(pytz.utc) - timedelta(days=14)
        # fresh_jobs = Job.objects.filter(pub_date__gte=one_week_ago, rejected=False)
        # if we see job type, we need to pass it along to context,
        # and also filter our fresh jobs by it.
        featured = Job.objects.filter(featured=True, pub_date__gte=fresh, rejected=False)
        if self.request.method == 'GET' and 'job_type' in self.request.GET:
           job_type = self.request.GET['job_type']
           context['job_type'] = (job_type, PRACTICE_CHOICES[job_type])
           #fresh_jobs = Job.objects.filter(pub_date__gte=one_week_ago, rejected=False, job_type=job_type)
           featured = featured.filter(
               job_type=job_type)
        context['highlighted'] = featured
        return context


class FreshJobListView(ListView):
    template_name = "jobsearch/fresh_job_list.html"

    def get_queryset(self):
        fresh = datetime.now(pytz.utc) - timedelta(days=10)
        return Job.objects.filter(pub_date__gte=fresh, rejected=False)
    

class CompanyDetailView(DetailView):
    model = Company


class JobDetailView(DetailView):
    model = Job

    def get_context_data(self, **kwargs):
        context = super(JobDetailView, self).get_context_data(**kwargs)
        
        return context


@login_required
def import_jobs(request):
    """
    First do any necessary clean-up, 
    and then search for new jobs.
    """
    user = request.user
    importers_dir = os.path.join(os.path.dirname(__file__), 'importers')
    expire_date = datetime.now(pytz.utc) - timedelta(days=40) # 30 is close enough for me.

    for job in Job.objects.all():
        # First, if the job is old, just delete it.
        # TO-DO: we're working around some naive datetimes here 
        # that should probably happen in the importer
        pub_date = job.pub_date
        if not pub_date.tzinfo:
            pub_date = pytz.utc.localize(pub_date)
        if pub_date <= expire_date:
            print("Deleting", job)
            job.delete()
            continue
        
        # now we'll ping the job and see if we get a 200. If not, delete it.
        # we don't bother doing this in debug because it's too intensitve.
        if settings.DEBUG is False:
            try:
                r = requests.get(job.link, headers=settings.IMPORTER_HEADERS, timeout=2)
                if r.status_code != 200:
                    print("Failed to find job: ", job, r.status_code)
                    job.delete()
                    continue
            except Exception as e:
                print('Failed to ping job', job, e)
                job.delete()
                continue
        # TO-DO: Build in detail getters here

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
        company, created = Company.objects.get_or_create(importer_name=job['company'])
        try:
            Job.objects.get(job_id=job['job_id'], new_company=company)
        except:
            try:
                print("importing ", job['company'], job['title'])
                
                newjob = Job (
                    title = job['title'],
                    link = job['link'],
                    #company = job['company'],
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