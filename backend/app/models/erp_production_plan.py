from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from app.core.database import Base


class ErpProductionPlan(Base):
    __tablename__ = "erp_production_plans"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    wo_no = Column(String, nullable=False, index=True)
    part_no = Column(String, nullable=False)
    planned_qty = Column(Numeric(14, 2), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, default="planned")
