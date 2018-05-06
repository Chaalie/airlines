from django import template
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    params = context['request'].GET.dict()
    params.update(kwargs)
    return "?" + urlencode(params)

@register.simple_tag(takes_context=True)
def query_string_to_form(context, *args, **kwargs):
    params = context['request'].GET.dict()
    params = {k:params[k] for k in params if k not in args}
    params.update(kwargs)
    inputs = '\n'.join([f'<input type="hidden" name={k} value={v}>'
                      for k, v in params.items()])
    return mark_safe(inputs)

@register.filter(name='addclass')
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})
