from django.shortcuts import render
from politician.models import Politician


def index(request):
    politicians = Politician.objects \
        .filter(active=True) \
        .all()

    return render(request, "politician/index.html", {
        "politicians": politicians
    })
