from django.db import models


class Submission(models.Model):
    PRODUCT_CHOICES = [
        ("churn_fitness", "Churn Fitness"),
        ("segmentation", "Segmentation"),
    ]

    email = models.EmailField()
    product = models.CharField(max_length=64, choices=PRODUCT_CHOICES, default="churn_fitness")

    # For now: store a path/key (later this will be a MinIO object key)
    file_path = models.CharField(max_length=512)

    # Wedge-specific configuration (e.g. churn_inactive_days)
    config_json = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Submission {self.id} ({self.product})"


class Run(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "PENDING"),
        ("RUNNING", "RUNNING"),
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
    ]

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="runs")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PENDING")

    verdict = models.CharField(max_length=16, null=True, blank=True)  # FIT/BORDERLINE/UNFIT
    pipeline_version = models.CharField(max_length=64, default="churn_fitness@0.1.0")
    
    result_json = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Run {self.id} ({self.status})"


class Artifact(models.Model):
    TYPE_CHOICES = [
        ("pdf", "PDF"),
        ("json", "JSON"),
        ("csv", "CSV"),
    ]

    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="artifacts")
    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    file_path = models.CharField(max_length=512)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Artifact {self.id} ({self.type})"
        