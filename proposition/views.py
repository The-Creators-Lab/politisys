from django.shortcuts import render
from rest_framework.decorators import api_view
from politician.factories import CongressServiceFactory


@api_view()
def get_proposition(request, proposition_at, proposition_id):
    service = CongressServiceFactory(proposition_at)
    proposition = service.get_proposition_by_id(proposition_id)

    return render(request, "proposition/proposition.html", {
        "proposition_at": proposition_at,
        "proposition": proposition
    })
