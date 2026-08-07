from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.email import EmailCreate, EmailOut
from app.services.email_generation import generate_email
from app.services.extraction import extract_text

router = APIRouter(tags=["email"])


@router.post("/documents/{document_id}/email", response_model=EmailOut)
def create_email(
    document_id: int,
    email_in: EmailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == current_user.id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    from app.api.documents import UPLOAD_DIR

    text = extract_text(UPLOAD_DIR / document.stored_filename, document.content_type)
    result = generate_email(text, email_in.tone.value, email_in.language.value, email_in.instructions)

    return EmailOut(subject=result["subject"], body=result["body"])
