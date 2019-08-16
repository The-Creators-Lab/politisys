from math import ceil
from django.shortcuts import render
from politician.models import Politician


def index(request):
    query = Politician.objects \
        .order_by("name") \
        .filter(active=True)

    search = request.GET.get("search")
    if search:
        query = query.filter(name__contains=search)

    page = int(request.GET.get("page", "1"))
    total = query.count()
    limit = 100
    offset = limit * (page - 1)
    total_pages = total / limit

    return render(request, "politician/index.html", {
        "politicians": query[offset:offset + limit],
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "page": page,
            "total_pages": ceil(total_pages),
            "pages": range(ceil(total_pages))
        }
    })
