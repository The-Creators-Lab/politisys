from math import ceil
from django.shortcuts import render
from politician.factories import CongressServiceFactory
from politician.services import PoliticianService


def index(request):
    page = int(request.GET.get("page", "1"))
    limit = 100

    service = PoliticianService()
    total, politicians, offset = service.get_list(
        limit=limit, page=page, search=request.GET.get("search"))

    total_pages = total / limit

    return render(request, "politician/index.html", {
        "politicians": politicians,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "page": page,
            "total_pages": ceil(total_pages),
            "pages": range(ceil(total_pages))
        }
    })


def profile(request, politician_id):
    service = PoliticianService()
    politician = service.get_by_id(politician_id)

    if not politician.birthdate:
        congress_service = CongressServiceFactory(politician.role)
        data = congress_service.get_by_id(politician.external_id)

        politician.birthdate = data["birthday"]
        politician.email = data["email"]
        politician.save()

    return render(request, "politician/profile.html", {
        "politician": politician
    })


def last_law_projects(request, politician_id):
    service = PoliticianService()
    politician = service.get_by_id(politician_id)

    congress_service = CongressServiceFactory(politician.role)
    last_law_projects = congress_service.get_last_law_projects(politician)

    return render(request, "politician/last_law_projects.html", {
        "last_law_projects": last_law_projects
    })
