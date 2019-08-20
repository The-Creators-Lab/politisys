from django.urls import path
from politician import views


urlpatterns = [
    path('', views.index, name="politician_index"),
    path('<int:politician_id>/profile',
         views.profile,
         name="politician_profile"),

    path('<int:politician_id>/last_law_projects',
         views.last_law_projects,
         name="politician_last_law_projects"),

    path('<int:politician_id>/total_expenses',
         views.get_total_expenses,
         name="politician_total_expenses"),
    path('<int:politician_id>/current_year_expenses',
         views.current_year_expenses,
         name="politician_current_year_expenses")
]
