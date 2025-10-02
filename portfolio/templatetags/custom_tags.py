from django import template


register = template.Library()


@register.filter("endswith")
def endswith(value, arg): return value.lower().endswith(arg.lower())
