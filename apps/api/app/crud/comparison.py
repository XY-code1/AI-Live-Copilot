from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comparison import (
    Comparison,
    ComparisonDifference,
    Competitor,
)
from app.schemas.comparison import (
    ComparisonCreate,
    CompetitorCreate,
    CompetitorUpdate,
    DifferenceCreate,
)


def list_competitors(db: Session, workspace_id: UUID) -> list[Competitor]:
    return list(db.scalars(select(Competitor).where(Competitor.workspace_id == workspace_id).order_by(Competitor.created_at.desc())).all())


def get_competitor(db: Session, competitor_id: UUID, workspace_id: UUID | None = None) -> Competitor | None:
    statement = select(Competitor).where(Competitor.id == competitor_id)
    if workspace_id is not None:
        statement = statement.where(Competitor.workspace_id == workspace_id)
    return db.scalar(statement)


def create_competitor(db: Session, payload: CompetitorCreate, workspace_id: UUID) -> Competitor:
    competitor = Competitor(**payload.model_dump(exclude={"workspace_id"}), workspace_id=workspace_id)
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return competitor


def update_competitor(db: Session, competitor: Competitor, payload: CompetitorUpdate) -> Competitor:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(competitor, field, value)
    db.commit()
    db.refresh(competitor)
    return competitor


def delete_competitor(db: Session, competitor: Competitor) -> None:
    db.delete(competitor)
    db.commit()


def list_comparisons(db: Session, product_id: UUID, workspace_id: UUID) -> list[Comparison]:
    statement = (
        select(Comparison)
        .where(Comparison.product_id == product_id, Comparison.workspace_id == workspace_id)
        .order_by(Comparison.created_at.desc())
    )
    return list(db.scalars(statement).all())


def list_all_comparisons(db: Session, workspace_id: UUID) -> list[Comparison]:
    statement = select(Comparison).where(Comparison.workspace_id == workspace_id).order_by(Comparison.created_at.desc())
    return list(db.scalars(statement).all())


def get_comparison(db: Session, comparison_id: UUID, workspace_id: UUID | None = None) -> Comparison | None:
    statement = select(Comparison).where(Comparison.id == comparison_id)
    if workspace_id is not None:
        statement = statement.where(Comparison.workspace_id == workspace_id)
    return db.scalar(statement)


def create_comparison(db: Session, payload: ComparisonCreate, workspace_id: UUID) -> Comparison:
    comparison = Comparison(**payload.model_dump(exclude={"workspace_id"}), workspace_id=workspace_id)
    db.add(comparison)
    db.commit()
    db.refresh(comparison)
    return comparison


def delete_comparison(db: Session, comparison: Comparison) -> None:
    db.delete(comparison)
    db.commit()


def add_difference(
    db: Session, comparison: Comparison, payload: DifferenceCreate
) -> ComparisonDifference:
    difference = ComparisonDifference(comparison_id=comparison.id, **payload.model_dump())
    db.add(difference)
    db.commit()
    db.refresh(difference)
    return difference


def get_difference(db: Session, difference_id: UUID) -> ComparisonDifference | None:
    return db.get(ComparisonDifference, difference_id)


def delete_difference(db: Session, difference: ComparisonDifference) -> None:
    db.delete(difference)
    db.commit()
