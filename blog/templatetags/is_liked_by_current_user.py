from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def is_liked_by_current_user(context, object):
  return object.is_liked_by(context['request'].user)
