from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func

from app.core.database import Base


class ErpMaterial(Base):
    __tablename__ = "erp_materials"
    __table_args__ = (UniqueConstraint("organization_id", "part_no", name="uq_erp_material_org_part"),)

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    part_no = Column(String, nullable=False)
    name = Column(String, nullable=False)
    uom = Column(String, nullable=True)
    safety_stock = Column(Numeric(14, 2), nullable=True)
    lead_time_days = Column(Integer, nullable=True)
    unit_price = Column(Numeric(14, 2), nullable=True)
    vendor_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
