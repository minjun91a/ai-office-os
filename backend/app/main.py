from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.qa import router as qa_router
from app.api.document_analysis import router as document_analysis_router
from app.api.report import router as report_router
from app.api.email import router as email_router
from app.api.agent import router as agent_router
from app.api.gmail import router as gmail_router

app = FastAPI(title="AI Office OS API")
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(qa_router)
app.include_router(document_analysis_router)
app.include_router(report_router)
app.include_router(email_router)
app.include_router(agent_router)
app.include_router(gmail_router)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "AI Office OS API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}