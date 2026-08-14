from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func

from app.core.database import Base


class QaLog(Base):
    __tablename__ = "qa_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
