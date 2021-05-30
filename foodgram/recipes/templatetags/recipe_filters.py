from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def tag_filtered(request, tag_slug):
    q_dict = request.GET.copy()
    if 'page' in q_dict:
        q_dict.pop('page')
    tags = q_dict.getlist('tags')
    if tag_slug in tags:
        tags.remove(tag_slug)
    else:
        tags.append(tag_slug)
    q_dict.setlist('tags', tags)

    return request.path + '?' + q_dict.urlencode()
