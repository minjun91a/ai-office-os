from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.api.deps import require_admin, require_superadmin
from app.core.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.models.api_log import ApiLog
from app.models.document import Document
from app.schemas.admin import (
    AdminUserOut,
    OrganizationCreate,
    OrganizationOut,
    UserActiveUpdate,
    UserOrganizationUpdate,
    AiUsageStatsOut,
    DocumentStatsOut,
    ErrorLogOut,
    OrganizationUsageOut,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _scoped_user_query(db: Session, current_user: User):
    query = db.query(User)
    if current_user.role != "superadmin":
        query = query.filter(User.organization_id == current_user.organization_id)
    return query


@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return _scoped_user_query(db, current_user).all()


@router.get("/users/{user_id}", response_model=AdminUserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = _scoped_user_query(db, current_user).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/users/{user_id}/active", response_model=AdminUserOut)
def update_user_active(
    user_id: int,
    update_in: UserActiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = _scoped_user_query(db, current_user).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = update_in.is_active
    db.commit()
    db.refresh(user)
    return user


@router.post("/organizations", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_in: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    organization = Organization(name=org_in.name)
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


@router.get("/organizations", response_model=list[OrganizationOut])
def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    return db.query(Organization).all()


@router.patch("/users/{user_id}/organization", response_model=AdminUserOut)
def update_user_organization(
    user_id: int,
    update_in: UserOrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    organization = db.query(Organization).filter(Organization.id == update_in.organization_id).first()
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    user.organization_id = organization.id
    db.commit()
    db.refresh(user)
    return user

AI_ENDPOINT_PATTERNS = {
    "qa": "/qa/ask",
    "document_analysis": "/documents/%/analyze",
    "report": "/documents/%/reports",
    "email": "/documents/%/email",
    "agent": "/agent/run",
    "gmail_draft": "/gmail/documents/%/gmail-draft",
}


def _scoped_document_query(db: Session, current_user: User):
    query = db.query(Document)
    if current_user.role != "superadmin":
        query = query.join(User, Document.owner_id == User.id).filter(
            User.organization_id == current_user.organization_id
        )
    return query


@router.get("/stats/documents", response_model=DocumentStatsOut)
def document_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = _scoped_document_query(db, current_user)
    total = query.count()

    type_counts = (
        query.with_entities(Document.content_type, func.count(Document.id))
        .group_by(Document.content_type)
        .all()
    )

    return DocumentStatsOut(
        total_documents=total,
        by_content_type={content_type: count for content_type, count in type_counts},
    )


@router.get("/stats/ai-usage", response_model=AiUsageStatsOut)
def ai_usage_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    base_query = db.query(ApiLog)
    if current_user.role != "superadmin":
        base_query = base_query.filter(ApiLog.organization_id == current_user.organization_id)

    by_endpoint = {
        name: base_query.filter(ApiLog.path.like(pattern)).count()
        for name, pattern in AI_ENDPOINT_PATTERNS.items()
    }

    return AiUsageStatsOut(
        total_ai_calls=sum(by_endpoint.values()),
        by_endpoint=by_endpoint,
    )

@router.get("/logs/errors", response_model=list[ErrorLogOut])
def list_error_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    limit: int = 50,
):
    query = db.query(ApiLog).filter(ApiLog.status_code >= 500)
    if current_user.role != "superadmin":
        query = query.filter(ApiLog.organization_id == current_user.organization_id)
    return query.order_by(ApiLog.id.desc()).limit(limit).all()

@router.get("/stats/organizations", response_model=list[OrganizationUsageOut])
def organization_usage_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    ai_call_filter = or_(*[ApiLog.path.like(p) for p in AI_ENDPOINT_PATTERNS.values()])

    def _usage_row(org_id: int | None, org_name: str) -> OrganizationUsageOut:
        user_count = db.query(User).filter(User.organization_id == org_id).count()
        document_count = (
            db.query(Document)
            .join(User, Document.owner_id == User.id)
            .filter(User.organization_id == org_id)
            .count()
        )
        ai_call_count = (
            db.query(ApiLog)
            .filter(ApiLog.organization_id == org_id, ai_call_filter)
            .count()
        )
        return OrganizationUsageOut(
            organization_id=org_id,
            organization_name=org_name,
            user_count=user_count,
            document_count=document_count,
            ai_call_count=ai_call_count,
        )

    results = [
        _usage_row(org.id, org.name)
        for org in db.query(Organization).all()
    ]

    unassigned_count = db.query(User).filter(User.organization_id.is_(None)).count()
    if unassigned_count > 0:
        results.append(_usage_row(None, "미배정"))

    return results
