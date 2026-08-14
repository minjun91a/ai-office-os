import re
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.erp_material import ErpMaterial
from app.models.erp_stock_snapshot import ErpStockSnapshot
from app.services.erp.metrics import MetricKey

PART_NO_PATTERN = re.compile(r"^[A-Z]{2,3}-\d{4}(-[A-Z])?$")


class ErpFact(BaseModel):
    part_no: str
    metric: MetricKey
    value: Decimal
    as_of: datetime | None
    source_table: str


def get_latest_stock(
    db: Session, organization_id: int, part_nos: list[str]
) -> dict[str, ErpStockSnapshot]:
    valid_part_nos = [p for p in part_nos if PART_NO_PATTERN.match(p)]
    if not valid_part_nos:
        return {}

    rows = (
        db.query(ErpStockSnapshot)
        .filter(
            ErpStockSnapshot.organization_id == organization_id,
            ErpStockSnapshot.part_no.in_(valid_part_nos),
        )
        .distinct(ErpStockSnapshot.part_no)
        .order_by(ErpStockSnapshot.part_no, ErpStockSnapshot.as_of.desc())
        .all()
    )
    return {row.part_no: row for row in rows}


def get_materials(
    db: Session, organization_id: int, part_nos: list[str]
) -> dict[str, ErpMaterial]:
    valid_part_nos = [p for p in part_nos if PART_NO_PATTERN.match(p)]
    if not valid_part_nos:
        return {}

    rows = (
        db.query(ErpMaterial)
        .filter(
            ErpMaterial.organization_id == organization_id,
            ErpMaterial.part_no.in_(valid_part_nos),
        )
        .all()
    )
    return {row.part_no: row for row in rows}


def query_facts(
    db: Session, organization_id: int, part_nos: list[str], metrics: list[MetricKey]
) -> list[ErpFact]:
    stock_by_part = get_latest_stock(db, organization_id, part_nos)
    material_by_part = get_materials(db, organization_id, part_nos)

    facts: list[ErpFact] = []
    for part_no in part_nos:
        if not PART_NO_PATTERN.match(part_no):
            continue

        if MetricKey.AVAILABLE_STOCK in metrics:
            snapshot = stock_by_part.get(part_no)
            if snapshot is not None:
                facts.append(ErpFact(
                    part_no=part_no, metric=MetricKey.AVAILABLE_STOCK,
                    value=snapshot.available_qty, as_of=snapshot.as_of,
                    source_table="erp_stock_snapshots",
                ))

        if MetricKey.SAFETY_STOCK in metrics:
            material = material_by_part.get(part_no)
            if material is not None and material.safety_stock is not None:
                facts.append(ErpFact(
                    part_no=part_no, metric=MetricKey.SAFETY_STOCK,
                    value=material.safety_stock, as_of=None,
                    source_table="erp_materials",
                ))

        # WEEKLY_DEMAND: 아직 소스 테이블이 없음(수요예측 테이블 미설계) — not_applicable로 취급.
        # COVERAGE_WEEKS도 weekly_demand에 의존하므로 여기선 계산 안 함(service.py 참조).

    return facts
