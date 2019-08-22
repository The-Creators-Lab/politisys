from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from politician.factories import CongressServiceFactory
from politician.services import PoliticianService
from reports.utils import MONTHS


@api_view()
def get_politician_total_expenses(request, politician_id):
    service = PoliticianService()
    politician = service.get_by_id(politician_id)

    total_expenses = 0
    congress_service = CongressServiceFactory(politician.role)
    for expense in congress_service.get_current_year_expenses(politician):
        total_expenses += expense["price"]

    return Response({
        "total": total_expenses,
        "total_formatted": '{:,.2f}'.format(total_expenses)
        .replace(",", "v")
        .replace(".", ",")
        .replace("v", ".")
    }, status.HTTP_200_OK)


@api_view()
def get_politician_expenses_by_year(request, politician_id):
    service = PoliticianService()
    politician = service.get_by_id(politician_id)

    report = {
        "xAxis": {
            "categories": MONTHS
        },
        "yAxis": {
            "min": 0,
            "title": {
                "text": "Gastos em R$"
            }
        },

        "series": [{
            "name": "Gastos",
            "color": "red",
            "data": [0 for i in range(len(MONTHS))]
        }]
    }

    congress_service = CongressServiceFactory(politician.role)
    for expense in congress_service.get_current_year_expenses(politician):
        if not expense["date"]:
            continue

        expense_month = int(expense["date"].strftime("%m")) - 1
        report["series"][0]["data"][expense_month] += expense["price"]

    return Response(report)


@api_view()
def get_proposition_votes(request, proposition_at, proposition_id):
    service = CongressServiceFactory(proposition_at)
    votes, votes_by_party, votes_by_result = service.get_proposition_votes_by_id(
        proposition_id)

    reports = {
        "votes": votes,
        "votes_by_party": votes_by_party,
        "votes_by_result": votes_by_result
    }

    return Response(reports)
