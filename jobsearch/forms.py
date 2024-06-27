from django.forms import ModelForm

from .models import Job


class JobStatusForm(ModelForm):
    class Meta:
        model = Job
        fields = ["status"]