from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.erp_bom import ErpBom
from app.models.erp_inbound_schedule import ErpInboundSchedule
from app.models.erp_material import ErpMaterial
from app.models.user import User
from app.schemas.erp import ErpBomNodeOut, ErpInboundScheduleOut, ErpMaterialOut, ErpSyncResult
from app.services.erp.repository import get_latest_stock
from app.services.erp.service import coverage_weeks

router = APIRouter(prefix="/erp", tags=["erp"])


def _material_status(coverage) -> str:
    if coverage is None:
        return "unknown"
    if coverage < 1.5:
        return "critical"
    if coverage < 2.5:
        return "warning"
    return "ok"


def _scoped_organization_id(current_user: User) -> int:
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="조직에 소속되어 있지 않아 ERP 데이터를 조회할 수 없습니다.",
        )
    return current_user.organization_id


@router.get("/materials", response_model=list[ErpMaterialOut])
def list_materials(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    organization_id = _scoped_organization_id(current_user)

    materials = (
        db.query(ErpMaterial)
        .filter(ErpMaterial.organization_id == organization_id, ErpMaterial.is_active.is_(True))
        .all()
    )
    part_nos = [m.part_no for m in materials]
    stock_by_part = get_latest_stock(db, organization_id, part_nos)

    results = []
    for material in materials:
        snapshot = stock_by_part.get(material.part_no)
        # weekly_demand 소스가 아직 없어 coverage_weeks는 항상 None (repository.py의 알려진 갭)
        coverage = coverage_weeks(snapshot.available_qty if snapshot else None, None)
        results.append(ErpMaterialOut(
            part_no=material.part_no, name=material.name, uom=material.uom,
            safety_stock=material.safety_stock,
            available_qty=snapshot.available_qty if snapshot else None,
            as_of=snapshot.as_of if snapshot else None,
            coverage_weeks=coverage,
            status=_material_status(coverage),
        ))
    return results


@router.get("/materials/{part_no}", response_model=ErpMaterialOut)
def get_material(part_no: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    organization_id = _scoped_organization_id(current_user)

    material = (
        db.query(ErpMaterial)
        .filter(ErpMaterial.organization_id == organization_id, ErpMaterial.part_no == part_no)
        .first()
    )
    if material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    stock_by_part = get_latest_stock(db, organization_id, [part_no])
    snapshot = stock_by_part.get(part_no)
    coverage = coverage_weeks(snapshot.available_qty if snapshot else None, None)

    return ErpMaterialOut(
        part_no=material.part_no, name=material.name, uom=material.uom,
        safety_stock=material.safety_stock,
        available_qty=snapshot.available_qty if snapshot else None,
        as_of=snapshot.as_of if snapshot else None,
        coverage_weeks=coverage,
        status=_material_status(coverage),
    )


@router.get("/bom/{part_no}", response_model=list[ErpBomNodeOut])
def get_bom(part_no: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    organization_id = _scoped_organization_id(current_user)

    rows = (
        db.query(ErpBom)
        .filter(ErpBom.organization_id == organization_id, ErpBom.parent_part_no == part_no)
        .all()
    )
    return [
        ErpBomNodeOut(
            parent_part_no=row.parent_part_no, child_part_no=row.child_part_no,
            qty_per=row.qty_per, level=row.level, alt_part_no=row.alt_part_no,
        )
        for row in rows
    ]


@router.get("/schedule", response_model=list[ErpInboundScheduleOut])
def get_schedule(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    organization_id = _scoped_organization_id(current_user)

    rows = db.query(ErpInboundSchedule).filter(ErpInboundSchedule.organization_id == organization_id).all()
    return [
        ErpInboundScheduleOut(
            po_no=row.po_no, part_no=row.part_no, qty=row.qty,
            original_eta=row.original_eta, current_eta=row.current_eta,
            status=row.status, vendor_name=row.vendor_name,
        )
        for row in rows
    ]


@router.post("/sync", response_model=ErpSyncResult)
def sync_erp(current_user: User = Depends(require_admin)):
    return ErpSyncResult(
        status="not_implemented",
        detail="실제 외부 ERP 연동이 없습니다. 데모 데이터는 scripts/seed_erp.py로 채워주세요.",
    )
