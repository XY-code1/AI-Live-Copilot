from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ingestion import IngestionRun, IngestionStatus


def start_run(
    db: Session,
    *,
    product_id: UUID,
    type: str,
    workspace_id: UUID | None,
    parser: str | None = None,
    requested_url: str | None = None,
) -> IngestionRun:
    run = IngestionRun(
        product_id=product_id,
        type=type,
        workspace_id=workspace_id,
        status=IngestionStatus.running.value,
        parser=parser,
        requested_url=requested_url,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def finish_run(
    db: Session,
    run: IngestionRun,
    *,
    source_id: UUID | None = None,
    content_hash: str | None = None,
    snapshot_path: str | None = None,
    final_url: str | None = None,
    redirect_chain: list[str] | None = None,
    fetch_duration_ms: int | None = None,
    raw_size_bytes: int | None = None,
    cleaned_text_length: int | None = None,
) -> IngestionRun:
    run.status = IngestionStatus.done.value
    run.source_id = source_id
    run.content_hash = content_hash
    run.snapshot_path = snapshot_path
    run.final_url = final_url
    run.fetch_duration_ms = fetch_duration_ms
    run.raw_size_bytes = raw_size_bytes
    run.cleaned_text_length = cleaned_text_length
    if redirect_chain is not None:
        run.redirect_chain = redirect_chain
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run


def fail_run(db: Session, run: IngestionRun, error: str) -> IngestionRun:
    run.status = IngestionStatus.failed.value
    run.error = error[:2000]
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run
