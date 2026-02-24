from django.urls import path
from core import views

urlpatterns = [
    # Minimal UI
    path("", views.upload_page, name="upload_page"),
    path("submit-ui/", views.submit_ui, name="submit_ui"),
    path("runs/<int:run_id>/page/", views.run_status_page, name="run_status_page"),

    # JSON API
    path("submit/", views.submit_csv, name="submit_csv"),
    path("runs/<int:run_id>/", views.run_status, name="run_status"),
]