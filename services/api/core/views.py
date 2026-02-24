import os
import uuid

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from core.enqueue import enqueue_run
from core.models import Submission, Run

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/data/uploads")


def _save_upload_to_disk(uploaded_file) -> str:
    """
    Saves an uploaded file to UPLOAD_DIR and returns the full filesystem path.
    API and worker both must share the same /data/uploads volume.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as out:
        for chunk in uploaded_file.chunks():
            out.write(chunk)

    return path


def _create_submission_and_run(email: str, file_path: str) -> Run:
    submission = Submission.objects.create(
        email=email,
        product="churn_fitness",
        file_path=file_path,
        config_json={"churn_inactive_days": 30},
    )

    run = Run.objects.create(
        submission=submission,
        status="PENDING",
        pipeline_version=f"{submission.product}@0.1.0",
    )

    enqueue_run(run.id)
    return run


# -----------------------------
# JSON API endpoints (existing)
# -----------------------------

@csrf_exempt
@require_POST
def submit_csv(request):
    email = request.POST.get("email")
    f = request.FILES.get("file")
    if not email or not f:
        return JsonResponse({"error": "email and file are required"}, status=400)

    path = _save_upload_to_disk(f)
    run = _create_submission_and_run(email=email, file_path=path)

    return JsonResponse(
        {
            "submission_id": run.submission_id,
            "run_id": run.id,
            "status_url": f"/runs/{run.id}/",
            "status_page_url": f"/runs/{run.id}/page/",
        }
    )


@require_GET
def run_status(request, run_id: int):
    run = get_object_or_404(Run, id=run_id)
    artifact = run.artifacts.filter(type="pdf").order_by("-id").first()

    return JsonResponse(
        {
            "run_id": run.id,
            "submission_id": run.submission_id,
            "status": run.status,
            "verdict": run.verdict,
            "error_message": run.error_message,
            "result_json": run.result_json,
            "pdf_object_key": artifact.file_path if artifact else None,
        }
    )


# -----------------------------
# Minimal UI (new)
# -----------------------------

@require_GET
def upload_page(request):
    return render(request, "core/upload.html")


@require_POST
def submit_ui(request):
    email = request.POST.get("email")
    f = request.FILES.get("file")
    if not email or not f:
        return render(request, "core/upload.html", {"error": "email and file are required"})

    path = _save_upload_to_disk(f)
    run = _create_submission_and_run(email=email, file_path=path)
    return redirect(f"/runs/{run.id}/page/")


@require_GET
def run_status_page(request, run_id: int):
    run = get_object_or_404(Run, id=run_id)
    artifact = run.artifacts.filter(type="pdf").order_by("-id").first()
    pdf_key = artifact.file_path if artifact else None

    return render(
        request,
        "core/run_status.html",
        {"run": run, "pdf_key": pdf_key},
    )