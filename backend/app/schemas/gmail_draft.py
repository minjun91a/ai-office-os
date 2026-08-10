from pydantic import BaseModel

from app.schemas.email import EmailLanguage, EmailTone


class GmailDraftCreate(BaseModel):
    to: str | None = None
    tone: EmailTone = EmailTone.polite
    language: EmailLanguage = EmailLanguage.ko
    instructions: str | None = None


class GmailDraftOut(BaseModel):
    draft_id: str
    subject: str
    body: str
