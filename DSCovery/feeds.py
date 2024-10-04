from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords

from jobsearch.models import Job


class JobFeed(Feed):
    title = "DSCovery Jobs"
    link = "/feeds/jobs/"
    description = "Jobs aggregated recently on DSCovery."

    def items(self):
        return Job.objects.order_by("-pub_date")[:50]

    def item_title(self, item):
        return "%s: %s" % (item.new_company, item.title)

    def item_lastupdated(self, item):
        return item.pub_date
    
    def item_link(self, item):
        return item.link