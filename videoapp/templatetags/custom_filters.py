from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value, args):
    """
    Replaces a substring with another string in a value.
    Usage: {{ value|replace:"old_string,new_string" }}
    """
    old, new = args.split(',')
    return value.replace(old, new)
