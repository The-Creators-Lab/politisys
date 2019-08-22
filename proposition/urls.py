from django.urls import path
from proposition import views


urlpatterns = [
    path('<str:proposition_at>/<int:proposition_id>',
         views.get_proposition,
         name="propositions_by_id")
]
