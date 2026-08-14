from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String

from app.core.database import Base


class ErpStockSnapshot(Base):
    __tablename__ = "erp_stock_snapshots"
    __table_args__ = (Index("ix_erp_stock_latest", "organization_id", "part_no", "as_of"),)

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    part_no = Column(String, nullable=False, index=True)
    available_qty = Column(Numeric(14, 2), nullable=False)
    allocated_qty = Column(Numeric(14, 2), nullable=True)
    as_of = Column(DateTime(timezone=True), nullable=False)
