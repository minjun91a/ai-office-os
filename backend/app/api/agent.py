from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agent.graph import build_agent_graph

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run", response_model=AgentResponse)
def run_agent(
    agent_in: AgentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owned_document_ids = [
        doc.id for doc in db.query(Document).filter(Document.owner_id == current_user.id).all()
    ]

    graph = build_agent_graph(db)

    initial_state = {
        "request": agent_in.request,
        "owner_id": current_user.id,
        "owned_document_ids": owned_document_ids,
        "plan": [],
        "current_step": 0,
        "document_id": None,
        "document_text": None,
        "summary": None,
        "email_subject": None,
        "email_body": None,
        "logs": [],
        "error": None,
        "retry_count": 0,
    }

    final_state = graph.invoke(initial_state)

    return AgentResponse(
        success=final_state.get("error") is None,
        summary=final_state.get("summary"),
        email_subject=final_state.get("email_subject"),
        email_body=final_state.get("email_body"),
        document_id=final_state.get("document_id"),
        logs=final_state.get("logs", []),
        error=final_state.get("error"),
    )
