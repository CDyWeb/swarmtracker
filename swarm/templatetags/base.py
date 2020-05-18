from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def build_absolute_uri(context, location):
    return context.request.build_absolute_uri(str(location))
