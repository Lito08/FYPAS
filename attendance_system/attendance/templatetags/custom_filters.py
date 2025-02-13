from django import template

register = template.Library()

@register.filter
def dict_key(dictionary, key):
    """Allows accessing dictionary values by key in Django templates"""
    return dictionary.get(key, None)
