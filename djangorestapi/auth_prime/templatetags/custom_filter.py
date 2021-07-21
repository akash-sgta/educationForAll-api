from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@register.filter(name='split')
@stringfilter
def split(value, arg):
    arg = arg.split(",")
    return value.split(arg[0])[int(arg[1])]
