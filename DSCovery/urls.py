"""
URL configuration for DSCovery project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from jobsearch.views import JobListView, JobDetailView, fetch_job_details, import_jobs, reject_job, update_job_status

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', JobListView.as_view(), name='jobs'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job_detail'),

    path('fetch-details/', fetch_job_details, name="fetch_job"),

    path('import-jobs/', import_jobs, name="import_jobs"),
    
    path('reject-job/', reject_job, name="reject_job"),
    path('update-job-status/', update_job_status, name="update_job_status"),

    path("pages/", include("django.contrib.flatpages.urls")),


]
