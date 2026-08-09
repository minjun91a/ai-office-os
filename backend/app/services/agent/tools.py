from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.email_generation import generate_email
from app.services.extraction import extract_text
from app.services.report_generation import generate_report
from app.services.vectorstore import search

from .state import AgentState


def search_document(state: AgentState, db: Session) -> dict:
    results = search(state["request"], state["owned_document_ids"])
    metadatas = results["metadatas"][0]
    if not metadatas:
        raise ValueError("요청과 관련된 문서를 찾지 못했습니다.")

    counts: dict[int, int] = {}
    for meta in metadatas:
        doc_id = meta["document_id"]
        counts[doc_id] = counts.get(doc_id, 0) + 1
    document_id = max(counts, key=counts.get)

    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise ValueError("검색된 문서를 DB에서 찾지 못했습니다.")

    from app.api.documents import UPLOAD_DIR

    text = extract_text(UPLOAD_DIR / document.stored_filename, document.content_type)

    return {"document_id": document_id, "document_text": text}


def summarize_document(state: AgentState, db: Session) -> dict:
    if not state.get("document_text"):
        raise ValueError("요약할 문서 텍스트가 없습니다. search_document를 먼저 실행해야 합니다.")

    result = generate_report(state["document_text"], "markdown_report")
    return {"summary": result["content"]}


def draft_email(state: AgentState, db: Session) -> dict:
    if not state.get("document_text"):
        raise ValueError("이메일 초안을 작성할 문서 텍스트가 없습니다. search_document를 먼저 실행해야 합니다.")

    result = generate_email(state["document_text"], "polite", "ko")
    return {"email_subject": result["subject"], "email_body": result["body"]}


TOOLS = {
    "search_document": search_document,
    "summarize_document": summarize_document,
    "draft_email": draft_email,
}

TOOL_DESCRIPTIONS = {
    "search_document": "사용자 요청과 관련된 문서를 검색해서 전체 텍스트를 가져옵니다. 다른 도구를 쓰기 전에 보통 가장 먼저 필요합니다.",
    "summarize_document": "이미 검색된 문서를 요약합니다. search_document 이후에만 사용 가능합니다.",
    "draft_email": "이미 검색된 문서 내용을 바탕으로 이메일 초안(제목+본문)을 작성합니다. search_document 이후에만 사용 가능합니다.",
}
