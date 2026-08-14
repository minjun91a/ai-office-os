from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.erp_production_plan import ErpProductionPlan
from app.schemas.erp import FieldDiff, ProductionOrderChange


class ProductionOrderSnapshot(BaseModel):
    wo_no: str
    start_date: datetime | None
    end_date: datetime | None
    status: str


def _serialize(value) -> str | None:
    return None if value is None else str(value)


def build_diff(before: BaseModel, after: BaseModel) -> list[FieldDiff]:
    b, a = before.model_dump(), after.model_dump()
    return [
        FieldDiff(field=key, before=_serialize(b.get(key)), after=_serialize(value))
        for key, value in a.items()
        if b.get(key) != value
    ]


def get_production_order(db: Session, organization_id: int, wo_no: str) -> ErpProductionPlan | None:
    return (
        db.query(ErpProductionPlan)
        .filter(ErpProductionPlan.organization_id == organization_id, ErpProductionPlan.wo_no == wo_no)
        .first()
    )


def preview_diff(order: ErpProductionPlan, changes: ProductionOrderChange) -> list[FieldDiff]:
    before = ProductionOrderSnapshot(
        wo_no=order.wo_no, start_date=order.start_date, end_date=order.end_date, status=order.status,
    )
    after = before.model_copy(update=changes.model_dump(exclude_none=True))
    return build_diff(before, after)


def apply_changes(db: Session, order: ErpProductionPlan, changes: ProductionOrderChange) -> None:
    for field, value in changes.model_dump(exclude_none=True).items():
        setattr(order, field, value)
    db.commit()
