import os
import pandas as pd
from django.utils import timezone
from core.models import Run, Artifact
from core.reporting import render_dummy_pdf
from core.storage import upload_file
from core.fitness import evaluate_events_fitness

def process_run(run_id: int) -> None:
    run = Run.objects.select_related("submission").get(id=run_id)
    submission = run.submission

    run.status = "RUNNING"
    run.started_at = timezone.now()
    run.save(update_fields=["status", "started_at"])

    try:
        df = pd.read_csv(submission.file_path)
        fitness_result = evaluate_events_fitness(df)
        verdict = fitness_result["verdict"]

        run.result_json = fitness_result
        run.verdict = verdict
        run.save(update_fields=["result_json", "verdict"])

        pdf_path = render_dummy_pdf(run.id, verdict, fitness_result=fitness_result)

        bucket = os.environ.get("MINIO_BUCKET", "keelshift")
        object_key = f"runs/{run.id}/report.pdf"

        upload_file(
            bucket=bucket,
            object_key=object_key,
            file_path=pdf_path,
            content_type="application/pdf",
        )

        Artifact.objects.create(run=run, type="pdf", file_path=object_key)

        run.status = "SUCCESS"
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "finished_at"])

    except Exception as e:
        run.status = "FAILED"
        run.error_message = f"{type(e).__name__}: {e}"
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "error_message", "finished_at"])
        raise