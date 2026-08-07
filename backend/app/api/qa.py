from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.qa import AnswerOut, QuestionIn, SourceOut
from app.services.qa import generate_answer
from app.services.vectorstore import search

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/ask", response_model=AnswerOut)
def ask_question(
    question_in: QuestionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    documents = db.query(Document).filter(Document.owner_id == current_user.id).all()
    document_ids = [doc.id for doc in documents]
    filename_by_id = {doc.id: doc.filename for doc in documents}

    results = search(question_in.question, document_ids)

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    answer = generate_answer(question_in.question, chunks)

    sources = [
        SourceOut(
            document_id=meta["document_id"],
            filename=filename_by_id.get(meta["document_id"], "알 수 없음"),
            chunk_text=chunk[:200],
        )
        for chunk, meta in zip(chunks, metadatas)
    ]

    return AnswerOut(answer=answer, sources=sources)