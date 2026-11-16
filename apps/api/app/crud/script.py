from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.script import Script, ScriptSection
from app.schemas.script import ScriptVersionCreate


def get_script(db: Session, script_id: UUID) -> Script | None:
    return db.get(Script, script_id)


def list_scripts(db: Session, product_id: UUID | None = None) -> list[Script]:
    statement = select(Script)
    if product_id is not None:
        statement = statement.where(Script.product_id == product_id)
    statement = statement.order_by(Script.created_at.desc())
    return list(db.scalars(statement).all())


def list_versions(db: Session, series_id: UUID) -> list[Script]:
    statement = (
        select(Script)
        .where(Script.series_id == series_id)
        .order_by(Script.version.desc())
    )
    return list(db.scalars(statement).all())


def latest_version(db: Session, series_id: UUID) -> int:
    versions = list_versions(db, series_id)
    return versions[0].version if versions else 0


def save_version(
    db: Session, script: Script, payload: ScriptVersionCreate
) -> Script:
    """Create a new version; unchanged sections keep their AI/manual origin."""
    previous_origin = {section.content: section.origin for section in script.sections}

    for _ in range(2):
        try:
            version = latest_version(db, script.series_id) + 1
            new_script = Script(
                series_id=script.series_id,
                workspace_id=script.workspace_id,
                product_id=script.product_id,
                comparison_id=script.comparison_id,
                version=version,
                title=payload.title or script.title,
                scenario=script.scenario,
                audience=script.audience,
                style=script.style,
                status=script.status,
            )
            db.add(new_script)
            db.flush()
            for position, item in enumerate(payload.sections):
                db.add(
                    ScriptSection(
                        script_id=new_script.id,
                        kind=item.kind,
                        title=item.title,
                        content=item.content,
                        position=position,
                        origin=previous_origin.get(item.content, "manual"),
                    )
                )
            db.commit()
            db.refresh(new_script)
            return new_script
        except IntegrityError:
            db.rollback()
    raise RuntimeError("版本冲突，请重试")


def delete_script_series(db: Session, script: Script) -> None:
    """Delete every version of a script series."""
    series = list(
        db.scalars(select(Script).where(Script.series_id == script.series_id)).all()
    )
    for item in series:
        db.delete(item)
    db.commit()
