from django import template


register = template.Library()


@register.filter
def add(value, number):
    return int(value) + int(number)


@register.filter
def sub(value, number):
    result = int(value) - int(number)
    return result if result >= 0 else 0
