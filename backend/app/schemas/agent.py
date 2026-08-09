from pydantic import BaseModel


class AgentRequest(BaseModel):
    request: str


class AgentResponse(BaseModel):
    success: bool
    summary: str | None = None
    email_subject: str | None = None
    email_body: str | None = None
    document_id: int | None = None
    logs: list[str]
    error: str | None = None
