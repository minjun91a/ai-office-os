from sqlalchemy import Column, ForeignKey, Index, Integer, Numeric, String

from app.core.database import Base


class ErpBom(Base):
    __tablename__ = "erp_boms"
    __table_args__ = (Index("ix_erp_bom_child", "organization_id", "child_part_no"),)

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    parent_part_no = Column(String, nullable=False)
    child_part_no = Column(String, nullable=False)
    qty_per = Column(Numeric(14, 4), nullable=False)
    level = Column(Integer, nullable=False, default=1)
    alt_part_no = Column(String, nullable=True)
