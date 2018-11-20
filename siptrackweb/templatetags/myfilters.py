from datetime import datetime

from django import template
from django.forms.fields import CheckboxInput

register = template.Library()

@register.filter(name='is_checkbox')
def is_checkbox(value):
    return isinstance(value, CheckboxInput)


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

@register.filter('date_from_timestamp')
def date_from_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp))

