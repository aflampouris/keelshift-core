import os, uuid
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.models import Submission, Run
from core.enqueue import enqueue_run

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/data/uploads")

@csrf_exempt
@require_POST
def submit_csv(request):
    email = request.POST.get("email")
    f = request.FILES.get("file")
    if not email or not f:
        return JsonResponse({"error": "email and file are required"}, status=400)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{f.name}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as out:
        for chunk in f.chunks():
            out.write(chunk)

    submission = Submission.objects.create(
        email=email,
        product="churn_fitness",
        file_path=path,
        config_json={"churn_inactive_days": 30},
    )

    run = Run.objects.create(
        submission=submission,
        status="PENDING",
        pipeline_version=f"{submission.product}@0.1.0",
    )

    job_id = enqueue_run(run.id)

    return JsonResponse({
        "submission_id": submission.id,
        "run_id": run.id,
        "job_id": job_id,
        "status_url": f"/runs/{run.id}/",
    })

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from core.models import Run

@require_GET
def run_status(request, run_id: int):
    run = get_object_or_404(Run, id=run_id)
    artifact = run.artifacts.filter(type="pdf").order_by("-id").first()

    return JsonResponse({
        "run_id": run.id,
        "submission_id": run.submission_id,
        "status": run.status,
        "verdict": run.verdict,
        "error_message": run.error_message,
        "result_json": run.result_json,
        "pdf_object_key": artifact.file_path if artifact else None,
    })