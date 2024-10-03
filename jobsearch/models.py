from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

#from profiles.models import LEVEL_CHOICES, WORKPLACE_TYPE_CHOICES
from localflavor.us.models import USStateField

RECENCY_CHOICES = {
    "r86400": "Past day",
    "r604800": "Past week",
    "r2592000": "Past month",
    "": "Any time",
}

COMPANY_SIZE_CHOICES = {
    "1-50": "1-50 employees",
    "51-200": "51-200 employees",
    "201-500": "201-500 employees",
    "501-1000": "501-1,000 employees",
}

STATUS_CHOICES = {
    "1": "Considering",
    "2": "Applied",
    "3": "Initial Contact",
    "4": "Completed Phone Screen",
    "0": "Not interested"
}

PRACTICE_CHOICES = {
    "office": "Back Office",
    "bd": "Business Development",
    "content": "Content & Communications",
    "data": "Data and Analytics",
    "delivery": "Delivery",
    "design": "Design and Research",
    "engineering":  "Engineering & Development",
    'help': "Help and Support",
    "product": "Product Management",
    "security": "Security",
    "other": "Other",
}

Profile = get_user_model()


class JobSearch(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    keywords = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = USStateField(max_length=20)
        
    def __str__(self):
        return self.keywords
    
    def location(self):
        return "%s, %s" % self.city, self.state


class Agency(models.Model):
    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)

    def __str__(self):
        return self.name



class Group(models.Model):
    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Company(models.Model):
    importer_name = models.CharField("Name", max_length=255, help_text="Must match the key from the importer")
    slug = models.SlugField(max_length=255, blank=True)
    company_size = models.CharField(choices=COMPANY_SIZE_CHOICES, max_length=20, blank=True, null=True)
    co_link = models.CharField(max_length=255, blank=True, null=True)
    affiliations = models.ManyToManyField(Group, blank=True)
    importer_type = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    about = models.TextField(blank=True, null=True)
    agencies = models.ManyToManyField(Agency, blank=True)

    class Meta:
        ordering = ["importer_name"]
        verbose_name_plural = "companies"
        
    def __str__(self):
        return self.importer_name
    
    def save(self, *args, **kwargs):
        self.slug= slugify(self.importer_name)
        super(Company, self).save(*args, **kwargs)    

    def get_absolute_url(self):
        return reverse("company_detail", kwargs={"slug": self.slug})
    

class Job(models.Model):
    title = models.CharField(max_length=255)
    new_company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    #company = models.CharField(max_length=255)

    location = models.CharField(max_length=255)
    link = models.URLField()
    pub_date = models.DateTimeField("date published", blank=True, null=True)
    import_date = models.DateTimeField(auto_now_add=True)
    job_id = models.CharField(max_length=255, editable=False)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    rejected = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=PRACTICE_CHOICES, blank=True, null=True)

    # Details
    skills = models.CharField(max_length=255, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    salary = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("job_detail", kwargs={"pk": self.pk})

    def get_source_url(self):
        return self.link
            


class JobTitle(models.Model):
    title = models.CharField(max_length=255)


class BlockedCompany(models.Model):
    company = models.CharField(max_length=200)
