from django.urls import path
from core.views import submit_csv

urlpatterns = [
    path("submit/", submit_csv, name="submit_csv"),
]