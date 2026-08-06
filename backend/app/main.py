from fastapi import FastAPI

app = FastAPI(title="AI Office OS API")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "AI Office OS API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}