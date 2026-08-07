from pydantic import BaseModel

class QuestionIn(BaseModel):
    question: str


class SourceOut(BaseModel):
    document_id: int
    filename: str
    chunk_text: str


class AnswerOut(BaseModel):
    answer: str
    sources: list[SourceOut]