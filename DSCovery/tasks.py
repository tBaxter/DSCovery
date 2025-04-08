from celery import shared_task
from django.core.management import call_command

@shared_task
def import_jobs():
    call_command('import_jobs')
from django.conf import settings
from django.utils import timezone
import requests
from bs4 import BeautifulSoup   
import re
import json
from datetime import datetime, timedelta
import pytz
import os
import logging