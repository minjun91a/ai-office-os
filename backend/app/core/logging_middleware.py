import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.api_log import ApiLog
from app.models.user import User

EXCLUDED_PATHS = {"/docs", "/redoc", "/openapi.json"}


class ApiLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        user_id = None
        organization_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")
            decoded_user_id = decode_access_token(token)
            if decoded_user_id is not None:
                user_id = int(decoded_user_id)

        db = SessionLocal()
        try:
            if user_id is not None:
                user = db.query(User).filter(User.id == user_id).first()
                if user is not None:
                    organization_id = user.organization_id

            db.add(ApiLog(
                user_id=user_id,
                organization_id=organization_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            ))
            db.commit()
        finally:
            db.close()

        return response
