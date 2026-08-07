from enum import Enum

from pydantic import BaseModel


class EmailTone(str, Enum):
    polite = "polite"
    concise = "concise"
    report = "report"


class EmailLanguage(str, Enum):
    ko = "ko"
    en = "en"


class EmailCreate(BaseModel):
    tone: EmailTone = EmailTone.polite
    language: EmailLanguage = EmailLanguage.ko
    instructions: str | None = None


class EmailOut(BaseModel):
    subject: str
    body: str