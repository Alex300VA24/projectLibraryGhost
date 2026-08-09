from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def nav_link(url_name, label, current):
    active = (url_name == current)
    link_class = 'nav-link text-brand-600 bg-brand-50 shadow-sm' if active else 'nav-link text-ink-600'
    url = reverse(url_name)
    return format_html(
        '<a href="{}" class="{}">{}</a>',
        url, link_class, label
    )
