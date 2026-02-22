from django.urls import path
from core.views import submit_csv, run_status

urlpatterns = [
    path("submit/", submit_csv, name="submit_csv"),
    path("runs/<int:run_id>/", run_status, name="run_status"),
]