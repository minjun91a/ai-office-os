from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    summary: str
    keywords: list[str]
    action_items: list[str]
    assignees: list[str]
    deadlines: list[str]
    importance: str
    is_meeting_minutes: bool
    meeting_summary: str | None
    created_at: datetime