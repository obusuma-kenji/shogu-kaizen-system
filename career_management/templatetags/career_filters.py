from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''
