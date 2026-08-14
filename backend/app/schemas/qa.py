from pydantic import BaseModel

class QuestionIn(BaseModel):
    question: str


class SourceOut(BaseModel):
    document_id: int
    filename: str
    chunk_text: str


class CrossCheckOut(BaseModel):
    metric_key: str
    entity_key: str
    verdict: str
    claimed_value: float | None
    erp_value: float | None


class AnswerOut(BaseModel):
    answer: str
    sources: list[SourceOut]
    cross_checks: list[CrossCheckOut] | None = None
