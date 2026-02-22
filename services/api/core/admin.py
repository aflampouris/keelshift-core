from django.contrib import admin
from .models import Submission, Run, Artifact


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "product", "created_at")
    search_fields = ("email",)
    ordering = ("-created_at",)


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "status",
        "verdict",
        "created_at",
        "finished_at",
    )
    list_filter = ("status", "verdict")
    ordering = ("-created_at",)
    readonly_fields = ("result_json", "error_message")


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "type", "created_at")
    ordering = ("-created_at",)