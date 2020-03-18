from django import template
from django.utils.safestring import mark_safe
from networks.models import Network,Station,Sta_ADSensor,Channel,Day_data

register = template.Library()  # register的名字是固定的,不可改变

@register.filter
def date2int(date):
    return date.year * 10000 + date.month * 100 + date.day

