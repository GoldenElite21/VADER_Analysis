import base64

from django import template

register = template.Library()

@register.filter
def to_base64(image):
    return base64.b64encode(image).decode('utf-8')
