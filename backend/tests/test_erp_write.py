import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.models.erp_production_plan import ErpProductionPlan
from app.models.organization import Organization
from app.schemas.erp import ProductionOrderChange
from app.services.agent.approval import requires_manual_approval
from app.services.erp.write import ProductionOrderSnapshot, apply_changes, build_diff, preview_diff


def test_diff_is_generated_from_schema():
    before = ProductionOrderSnapshot(
        wo_no="WO-5521", start_date=datetime(2026, 8, 10, tzinfo=timezone.utc), end_date=None, status="planned",
    )
    after = before.model_copy(update={"start_date": datetime(2026, 8, 14, tzinfo=timezone.utc)})

    diffs = build_diff(before, after)

    assert len(diffs) == 1
    assert diffs[0].field == "start_date"


def test_requires_manual_approval_for_erp_write():
    assert requires_manual_approval("erp_update_production_order") is True
    assert requires_manual_approval("search_document") is False


def test_erp_write_requires_approval(db_session):
    org = Organization(name=f"write-org-{uuid.uuid4().hex[:8]}")
    db_session.add(org)
    db_session.commit()

    order = ErpProductionPlan(
        organization_id=org.id, wo_no="WO-5521", part_no="PN-4471-A",
        planned_qty=Decimal("100"), start_date=datetime(2026, 8, 10, tzinfo=timezone.utc), status="planned",
    )
    db_session.add(order)
    db_session.commit()

    change = ProductionOrderChange(start_date=datetime(2026, 8, 14, tzinfo=timezone.utc))

    diffs = preview_diff(order, change)
    assert len(diffs) == 1
    db_session.refresh(order)
    assert order.start_date == datetime(2026, 8, 10, tzinfo=timezone.utc)  # 미리보기만 했으니 그대로

    apply_changes(db_session, order, change)
    db_session.refresh(order)
    assert order.start_date == datetime(2026, 8, 14, tzinfo=timezone.utc)  # 승인 후에야 바뀜
