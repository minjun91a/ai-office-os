from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.report import Report
from app.models.user import User
from app.schemas.report import ReportCreate, ReportOut
from app.services.extraction import extract_text
from app.services.report_generation import generate_report

router = APIRouter(tags=["reports"])


def _get_owned_document(document_id: int, db: Session, current_user: User) -> Document:
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == current_user.id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.post(
    "/documents/{document_id}/reports",
    response_model=ReportOut,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    document_id: int,
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = _get_owned_document(document_id, db, current_user)

    from app.api.documents import UPLOAD_DIR

    text = extract_text(UPLOAD_DIR / document.stored_filename, document.content_type)
    result = generate_report(text, report_in.report_type.value, report_in.instructions)

    report = Report(
        document_id=document_id,
        report_type=report_in.report_type.value,
        title=result["title"],
        content=result["content"],
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/documents/{document_id}/reports", response_model=list[ReportOut])
def list_reports(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_document(document_id, db, current_user)
    return db.query(Report).filter(Report.document_id == document_id).all()


@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = (
        db.query(Report)
        .join(Document, Report.document_id == Document.id)
        .filter(Report.id == report_id, Document.owner_id == current_user.id)
        .first()
    )
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.get("/reports/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = (
        db.query(Report)
        .join(Document, Report.document_id == Document.id)
        .filter(Report.id == report_id, Document.owner_id == current_user.id)
        .first()
    )
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    return Response(
        content=report.content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="report-{report_id}.md"'},
    )
