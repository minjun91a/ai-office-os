from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func

from app.core.database import Base


class CrossCheck(Base):
    __tablename__ = "cross_checks"

    id = Column(Integer, primary_key=True, index=True)
    qa_log_id = Column(Integer, ForeignKey("qa_logs.id"), nullable=False, index=True)

    metric_key = Column(String, nullable=False)
    entity_key = Column(String, nullable=False)

    claimed_value = Column(Numeric(18, 4), nullable=True)
    claimed_source = Column(String, nullable=True)
    claimed_as_of = Column(DateTime(timezone=True), nullable=True)

    erp_value = Column(Numeric(18, 4), nullable=True)
    erp_as_of = Column(DateTime(timezone=True), nullable=True)

    verdict = Column(String, nullable=False)
    delta = Column(Numeric(18, 4), nullable=True)
    tolerance = Column(Numeric(6, 4), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
