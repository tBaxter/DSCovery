import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

now = datetime.datetime.now()
one_day_ago = now - datetime.timedelta(days=1)

def site_processor(request):
    authenticated_request = request.user.is_authenticated
    last_seen = request.session.get('last_seen', now)

    return {
        'site': get_current_site(request),
        'now': now,
        'project_name': getattr(settings, 'PROJECT_NAME', None),
        'current_path': request.get_full_path(),
        'last_seen': last_seen,
        'authenticated_request': authenticated_request,
    }
