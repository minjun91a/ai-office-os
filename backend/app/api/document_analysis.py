from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.document_analysis import DocumentAnalysis
from app.models.user import User
from app.schemas.document_analysis import AnalysisOut
from app.services.document_analysis import analyze_document
from app.services.extraction import extract_text

router = APIRouter(prefix="/documents", tags=["document-analysis"])


@router.post(
    "/{document_id}/analyze",
    response_model=AnalysisOut,
    status_code=status.HTTP_201_CREATED,
)
def analyze(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == current_user.id)
        .first()
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    file_path = document.stored_filename
    from app.api.documents import UPLOAD_DIR

    text = extract_text(UPLOAD_DIR / file_path, document.content_type)
    result = analyze_document(text)

    analysis = (
        db.query(DocumentAnalysis)
        .filter(DocumentAnalysis.document_id == document_id)
        .first()
    )
    if analysis is None:
        analysis = DocumentAnalysis(document_id=document_id, **result)
        db.add(analysis)
    else:
        for key, value in result.items():
            setattr(analysis, key, value)

    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/{document_id}/analysis", response_model=AnalysisOut)
def get_analysis(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == current_user.id)
        .first()
    )
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    analysis = (
        db.query(DocumentAnalysis)
        .filter(DocumentAnalysis.document_id == document_id)
        .first()
    )
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found"
        )

    return analysis
