from django.urls import path
from reports import views


urlpatterns = [
    path('politician/<int:politician_id>/total_expenses',
         views.get_politician_total_expenses,
         name="reports_politician_total_expenses"),
    path('politician/<int:politician_id>/expenses',
         views.get_politician_expenses_by_year,
         name="reports_politician_expenses_by_year"),

    path('proposition/<str:proposition_at>/<int:proposition_id>/votes',
         views.get_proposition_votes,
         name="reports_proposition_votes")
]
