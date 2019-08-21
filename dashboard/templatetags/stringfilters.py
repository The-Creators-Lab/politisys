from json import dumps
from django.core.serializers import serialize, json
from django.db.models.query import QuerySet
from django import template


register = template.Library()


@register.filter
def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)

    return dumps(object, cls=json.DjangoJSONEncoder)
