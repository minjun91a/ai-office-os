from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router

app = FastAPI(title="AI Office OS API")
app.include_router(auth_router)
app.include_router(documents_router)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "AI Office OS API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}