import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.core.security import hash_password
from app.models.document import Document
from app.models.erp_stock_snapshot import ErpStockSnapshot
from app.models.organization import Organization
from app.models.user import User
from app.schemas.qa import AnswerOut, SourceOut
from app.services.trust.cross_validator import run_cross_check


def _make_user(db_session, organization_id=None):
    user = User(
        email=f"cross-test-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("testpassword123"),
        organization_id=organization_id,
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_stale_document_is_detected(db_session):
    org = Organization(name=f"cross-org-{uuid.uuid4().hex[:8]}")
    db_session.add(org)
    db_session.commit()
    user = _make_user(db_session, organization_id=org.id)

    document = Document(
        filename="test.pdf", stored_filename=f"{uuid.uuid4().hex}.pdf",
        content_type="application/pdf", file_size=100, owner_id=user.id,
        uploaded_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
    )
    db_session.add(document)
    db_session.commit()

    db_session.add(ErpStockSnapshot(
        organization_id=org.id, part_no="PN-4471-A",
        available_qty=Decimal("285"), as_of=datetime(2026, 8, 7, tzinfo=timezone.utc),
    ))
    db_session.commit()

    answer = AnswerOut(
        answer="PN-4471-A 가용재고 320 EA입니다.",
        sources=[SourceOut(document_id=document.id, filename="test.pdf", chunk_text="PN-4471-A 가용재고 320 EA")],
    )

    result = run_cross_check(db=db_session, user=user, question="재고 얼마야?", result=answer)

    check = next(c for c in result.cross_checks if c.metric_key == "available_stock")
    assert check.verdict == "stale_document"
    assert "285" in result.answer


def test_no_claims_returns_empty_cross_checks(db_session):
    org = Organization(name=f"cross-org-{uuid.uuid4().hex[:8]}")
    db_session.add(org)
    db_session.commit()
    user = _make_user(db_session, organization_id=org.id)

    answer = AnswerOut(answer="이번 회의 분위기 좋았습니다.", sources=[])
    result = run_cross_check(db=db_session, user=user, question="회의 어땠어?", result=answer)

    assert result.answer == answer.answer
    assert result.cross_checks == []


def test_flag_off_keeps_legacy_response_shape(client, monkeypatch):
    monkeypatch.setenv("ERP_CROSS_CHECK_ENABLED", "false")

    import app.api.qa as qa_module
    monkeypatch.setattr(qa_module, "generate_answer", lambda question, chunks: "기존 답변")
    monkeypatch.setattr(qa_module, "search", lambda question, document_ids: {"documents": [[]], "metadatas": [[]]})

    email = f"qa-flag-{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword123"
    client.post("/auth/signup", json={"email": email, "password": password})
    token = client.post("/auth/login", data={"username": email, "password": password}).json()["access_token"]

    response = client.post("/qa/ask", json={"question": "질문"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["cross_checks"] is None


def test_erp_failure_does_not_break_qa(client, monkeypatch):
    monkeypatch.setenv("ERP_CROSS_CHECK_ENABLED", "true")

    import app.api.qa as qa_module
    monkeypatch.setattr(qa_module, "generate_answer", lambda question, chunks: "테스트 답변입니다.")
    monkeypatch.setattr(qa_module, "search", lambda question, document_ids: {"documents": [[]], "metadatas": [[]]})

    def _boom(**kwargs):
        raise RuntimeError("ERP down")
    monkeypatch.setattr(qa_module, "run_cross_check", _boom)

    email = f"qa-fail-{uuid.uuid4().hex[:8]}@example.com"
    password = "testpassword123"
    client.post("/auth/signup", json={"email": email, "password": password})
    token = client.post("/auth/login", data={"username": email, "password": password}).json()["access_token"]

    response = client.post("/qa/ask", json={"question": "테스트 질문"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["answer"] == "테스트 답변입니다."
