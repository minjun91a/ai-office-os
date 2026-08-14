from datetime import datetime

from pydantic import BaseModel


class ErpMaterialOut(BaseModel):
    part_no: str
    name: str
    uom: str | None
    safety_stock: float | None
    available_qty: float | None
    as_of: datetime | None
    coverage_weeks: float | None
    status: str  # critical / warning / ok / unknown


class ErpBomNodeOut(BaseModel):
    parent_part_no: str
    child_part_no: str
    qty_per: float
    level: int
    alt_part_no: str | None


class ErpInboundScheduleOut(BaseModel):
    po_no: str
    part_no: str
    qty: float
    original_eta: datetime | None
    current_eta: datetime | None
    status: str
    vendor_name: str | None


class ErpSyncResult(BaseModel):
    status: str
    detail: str
