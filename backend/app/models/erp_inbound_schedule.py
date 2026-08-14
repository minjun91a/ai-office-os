from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from app.core.database import Base


class ErpInboundSchedule(Base):
    __tablename__ = "erp_inbound_schedules"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    po_no = Column(String, nullable=False)
    part_no = Column(String, nullable=False, index=True)
    qty = Column(Numeric(14, 2), nullable=False)
    original_eta = Column(DateTime(timezone=True), nullable=True)
    current_eta = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, default="scheduled")
    vendor_name = Column(String, nullable=True)
