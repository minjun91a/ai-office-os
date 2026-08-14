import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.models.organization import Organization
from app.models.erp_stock_snapshot import ErpStockSnapshot
from app.services.erp.repository import PART_NO_PATTERN, get_latest_stock
from app.services.erp.service import coverage_weeks


def test_erp_query_rejects_injected_part_no():
    assert not PART_NO_PATTERN.match("PN-4471-A'; DROP TABLE--")


def test_get_latest_stock_is_org_scoped(db_session):
    org_a = Organization(name=f"org-a-{uuid.uuid4().hex[:8]}")
    org_b = Organization(name=f"org-b-{uuid.uuid4().hex[:8]}")
    db_session.add_all([org_a, org_b])
    db_session.commit()

    db_session.add(ErpStockSnapshot(
        organization_id=org_a.id, part_no="PN-1234",
        available_qty=Decimal("100"), as_of=datetime.now(timezone.utc),
    ))
    db_session.commit()

    result = get_latest_stock(db_session, organization_id=org_b.id, part_nos=["PN-1234"])
    assert result == {}


def test_get_latest_stock_returns_most_recent_snapshot(db_session):
    org = Organization(name=f"org-{uuid.uuid4().hex[:8]}")
    db_session.add(org)
    db_session.commit()

    old_time = datetime(2026, 8, 3, tzinfo=timezone.utc)
    new_time = datetime(2026, 8, 7, tzinfo=timezone.utc)
    db_session.add_all([
        ErpStockSnapshot(organization_id=org.id, part_no="PN-1234", available_qty=Decimal("320"), as_of=old_time),
        ErpStockSnapshot(organization_id=org.id, part_no="PN-1234", available_qty=Decimal("285"), as_of=new_time),
    ])
    db_session.commit()

    result = get_latest_stock(db_session, organization_id=org.id, part_nos=["PN-1234"])
    assert result["PN-1234"].available_qty == Decimal("285")


def test_coverage_weeks_returns_none_when_demand_is_zero():
    assert coverage_weeks(Decimal("100"), Decimal("0")) is None


def test_coverage_weeks_computes_correctly():
    assert coverage_weeks(Decimal("100"), Decimal("50")) == Decimal("2")
