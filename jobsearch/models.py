from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

#from profiles.models import LEVEL_CHOICES, WORKPLACE_TYPE_CHOICES
from localflavor.us.models import USStateField

RECENCY_CHOICES = {
    "r86400": "Past day",
    "r604800": "Past week",
    "r2592000": "Past month",
    "": "Any time",
}

STATUS_CHOICES = {
    "1": "Considering",
    "2": "Applied",
    "3": "Initial Contact",
    "4": "Completed Phone Screen",
    "0": "Not interested"

}

Profile = get_user_model()

class JobSearch(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    keywords = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = USStateField(max_length=20)
#    workplace_type = models.CharField(max_length=1, choices=WORKPLACE_TYPE_CHOICES)
#    level = models.CharField(max_length=1, choices=LEVEL_CHOICES, blank=True, null=True)
#    recency = models.CharField(max_length=10, choices=RECENCY_CHOICES, blank=True, null=True)
        
    def __str__(self):
        return self.keywords
    
    def location(self):
        return "%s, %s" % self.city, self.state

class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    link = models.URLField()
    pub_date = models.DateTimeField("date published", blank=True, null=True)
    salary = models.CharField(max_length=200, blank=True, null=True)
    import_date = models.DateTimeField(auto_now_add=True)
    job_id = models.CharField(max_length=200, editable=False)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    rejected = models.BooleanField(default=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, blank=True, null=True)

    # Details
    company_size = models.CharField(max_length=20, blank=True, null=True)
    skills = models.CharField(max_length=200, blank=True, null=True)
    co_link = models.CharField(max_length=200, blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("job_detail", kwargs={"pk": self.pk})

    def get_source_url(self):
        # Linkedin
        return "https://linkedin.com/jobs/view/{}/".format(self.job_id)
            


class JobTitle(models.Model):
    title = models.CharField(max_length=200)


class BlockedCompany(models.Model):
    company = models.CharField(max_length=200)
