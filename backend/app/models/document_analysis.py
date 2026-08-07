from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func

from app.core.database import Base


class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), unique=True, nullable=False)

    summary = Column(Text, nullable=False)
    keywords = Column(JSON, nullable=False)
    action_items = Column(JSON, nullable=False)
    assignees = Column(JSON, nullable=False)
    deadlines = Column(JSON, nullable=False)
    importance = Column(String, nullable=False)
    is_meeting_minutes = Column(Boolean, default=False, nullable=False)
    meeting_summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())