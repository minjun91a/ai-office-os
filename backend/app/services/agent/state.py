import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict):
    request: str
    owner_id: int
    owned_document_ids: list[int]
    plan: list[str]
    current_step: int
    document_id: int | None
    document_text: str | None
    summary: str | None
    email_subject: str | None
    email_body: str | None
    logs: Annotated[list[str], operator.add]
    error: str | None
    retry_count: int
