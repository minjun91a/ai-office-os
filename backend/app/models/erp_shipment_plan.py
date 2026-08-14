from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from app.core.database import Base


class ErpShipmentPlan(Base):
    __tablename__ = "erp_shipment_plans"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    so_no = Column(String, nullable=False, index=True)
    customer = Column(String, nullable=False)
    part_no = Column(String, nullable=False)
    qty = Column(Numeric(14, 2), nullable=False)
    requested_date = Column(DateTime(timezone=True), nullable=True)
    confirmed_date = Column(DateTime(timezone=True), nullable=True)
