from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.services.google_oauth import build_authorization_url, exchange_code_and_save
from app.schemas.gmail_draft import GmailDraftCreate, GmailDraftOut
from app.services.gmail_draft import create_draft
from app.models.document import Document
from app.models.user import User
from app.services.email_generation import generate_email
from app.services.extraction import extract_text
from app.api.deps import get_current_user


router = APIRouter(prefix="/gmail", tags=["gmail"])


@router.get("/login")
def gmail_login(token: str = Query(...)):
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.")

    authorization_url = build_authorization_url(state=token)
    return RedirectResponse(authorization_url)


@router.get("/callback")
def gmail_callback(code: str, state: str, db: Session = Depends(get_db)):
    user_id = decode_access_token(state)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 상태값입니다.")

    exchange_code_and_save(code=code, user_id=int(user_id), db=db)

    return {"message": "Gmail 연동이 완료되었습니다. 이 창을 닫으셔도 됩니다."}

@router.post("/documents/{document_id}/gmail-draft", response_model=GmailDraftOut)
def create_gmail_draft(
    document_id: int,
    draft_in: GmailDraftCreate,
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
    email_result = generate_email(text, draft_in.tone.value, draft_in.language.value, draft_in.instructions)

    try:
        draft_id = create_draft(
            user_id=current_user.id,
            db=db,
            to=draft_in.to,
            subject=email_result["subject"],
            body=email_result["body"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return GmailDraftOut(draft_id=draft_id, subject=email_result["subject"], body=email_result["body"])
