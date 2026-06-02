from django import template

register = template.Library()


@register.simple_tag
def breadcrumbs(request):
    path = request.path.strip("/").split("/")
    breadcrumbs = []
    url = ""

    for part in path:
        url += "/" + part
        breadcrumbs.append({"name": part.capitalize(), "url": url})

    return breadcrumbs
