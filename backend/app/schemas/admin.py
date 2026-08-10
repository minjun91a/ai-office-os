from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


class OrganizationCreate(BaseModel):
    name: str


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    organization_id: int | None
    is_active: bool
    created_at: datetime


class UserActiveUpdate(BaseModel):
    is_active: bool


class UserOrganizationUpdate(BaseModel):
    organization_id: int

class DocumentStatsOut(BaseModel):
    total_documents: int
    by_content_type: dict[str, int]


class AiUsageStatsOut(BaseModel):
    total_ai_calls: int
    by_endpoint: dict[str, int]


class ErrorLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    method: str
    path: str
    status_code: int
    duration_ms: int
    created_at: datetime

class OrganizationUsageOut(BaseModel):
    organization_id: int | None
    organization_name: str
    user_count: int
    document_count: int
    ai_call_count: int
