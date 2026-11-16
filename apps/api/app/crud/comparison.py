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


def list_competitors(db: Session) -> list[Competitor]:
    return list(db.scalars(select(Competitor).order_by(Competitor.created_at.desc())).all())


def get_competitor(db: Session, competitor_id: UUID) -> Competitor | None:
    return db.get(Competitor, competitor_id)


def create_competitor(db: Session, payload: CompetitorCreate) -> Competitor:
    competitor = Competitor(**payload.model_dump())
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


def list_comparisons(db: Session, product_id: UUID) -> list[Comparison]:
    statement = (
        select(Comparison)
        .where(Comparison.product_id == product_id)
        .order_by(Comparison.created_at.desc())
    )
    return list(db.scalars(statement).all())


def list_all_comparisons(db: Session) -> list[Comparison]:
    statement = select(Comparison).order_by(Comparison.created_at.desc())
    return list(db.scalars(statement).all())


def get_comparison(db: Session, comparison_id: UUID) -> Comparison | None:
    return db.get(Comparison, comparison_id)


def create_comparison(db: Session, payload: ComparisonCreate) -> Comparison:
    comparison = Comparison(**payload.model_dump())
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
