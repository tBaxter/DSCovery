import datetime

from django import template
from django.utils.timesince import timesince

register = template.Library()


@register.inclusion_tag('includes/formatted_time.html')
def format_time(date_obj, time_obj=None, datebox=False, dt_type=None, classes=None):
    """
    Returns formatted HTML5 elements based on given datetime object.
    By default returns a time element, but will return a .datebox if requested.

    dt_type allows passing dt_start or dt_end for hcal formatting.
    link allows passing a url to the datebox.

    classes allows sending arbitrary classnames. Useful for properly microformatting elements.

    Usage::

        {% format_time obj.pub_date %}
        {% format_time obj.start_date 'datebox' 'dtstart' %}
        {% format_time obj.end_date obj.end_time 'datebox' 'dt_end' %}
    
    """
    if not time_obj:
        time_obj = getattr(date_obj, 'time', None)

    if dt_type:
        classes = '{0} {1}'.format(classes, dt_type)
    if datebox:
        classes = '{0} {1}'.format(classes, datebox)
    return {
        'date_obj': date_obj,
        'time_obj': time_obj,
        'datebox': datebox,
        'current_year': datetime.date.today().year,
        'classes': classes
    }


@register.filter
def short_timesince(date):
    """
    A shorter version of Django's built-in timesince filter.
    Selects only the first part of the returned string,
    splitting on the comma.

    Falls back on default Django timesince if it fails.

    Example: 3 days, 20 hours becomes "3 days".

    """
    try:
        t = timesince(date).split(", ")[0]
    except IndexError:
        t = timesince(date)
    return t

