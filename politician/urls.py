from django.urls import path
from politician import views


urlpatterns = [
    path('', views.index, name="politician_index"),
    path('<int:politician_id>/profile', views.profile, name="politician_profile")
]
