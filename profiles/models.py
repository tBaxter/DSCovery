import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import PasswordInput
from django.urls import reverse
from django.utils.html import strip_tags

from localflavor.us.models import USStateField, USZipCodeField

#from tango_shared.models import set_img_path
#from tango_shared.utils.sanetize import sanetize_text
#from tango_shared.utils.maptools import get_geocode


WORKPLACE_TYPE_CHOICES = {
    "1": "On-site",
    "2": "Remote",
    "3": "Hybrid",
}

LEVEL_CHOICES = {
    "1": "Internship",
    "2": "Entry-level",
    "3": "Associate",
    "4": "Mid-Senior",
    "5": "Director",
    "6": "Executive",
}

class Profile(AbstractUser):
    """
    Subclasses AbstractUser to provide site-specific user fields.
    """
    street_address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional. Intended for mapping and/or pre-filling applications.")
    city = models.CharField(max_length=200)
    state = USStateField(max_length=20)
    zipcode = USZipCodeField(
        'ZIP/Postal Code',
        max_length=10,
        blank=True,
    )
    homepage = models.URLField('Your web site', blank=True)
    geocode = models.CharField(max_length=200, null=True, blank=True)

    linkedin_username = models.CharField(max_length=200, null=True, blank=True, help_text="Optional. Authenticated LinkedIn search shows much better results.")
    linkedin_password = models.CharField(max_length=200, null=True, blank=True, help_text="Optional. Authenticated LinkedIn search shows much better results.")

    # Preferences
    keywords = models.CharField("Job search keywords/title", max_length=200)
    workplace_type = models.CharField(max_length=1, choices=WORKPLACE_TYPE_CHOICES)
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES)

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        """
        TO-DO: Implement geocoding later
        needs_geocode = False
        if self.id is None:  # For new user, only set a few things:
            self.display_name = self.get_display_name()
            needs_geocode = True
        else:
            old_self = self.__class__.objects.get(id = self.id)
            if old_self.city != self.city or old_self.state != self.state or self.geocode is None:
                needs_geocode = True
            if old_self.display_name != self.display_name or old_self.first_name != self.first_name or old_self.last_name != self.last_name:
                self.display_name = self.get_display_name()  # check if display name has changed
            if old_self.avatar and old_self.avatar != self.avatar:
                os.remove(old_self.avatar.path)
        if self.city and self.state and needs_geocode:
            geocode = get_geocode(self.city, self.state, street_address=self.street_address, zipcode=self.zip)
            if geocode and geocode != '620':
                self.geocode = ', '.join(geocode)
        """
        super(Profile, self).save(*args, **kwargs)
