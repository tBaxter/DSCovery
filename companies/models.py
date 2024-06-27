from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=200)
    import_jobs = models.BooleanField(default=False)