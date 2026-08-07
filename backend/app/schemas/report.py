from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ReportType(str, Enum):
    markdown_report = "markdown_report"
    meeting_minutes = "meeting_minutes"
    work_report = "work_report"
    ppt_outline = "ppt_outline"
    word_outline = "word_outline"


class ReportCreate(BaseModel):
    report_type: ReportType
    instructions: str | None = None


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    report_type: str
    title: str
    content: str
    created_at: datetime