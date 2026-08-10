import base64
import os
from datetime import datetime, timezone
from email.mime.text import MIMEText

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.models.google_credential import GoogleCredential

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def _get_gmail_client(user_id: int, db: Session):
    credential = db.query(GoogleCredential).filter(GoogleCredential.user_id == user_id).first()
    if credential is None:
        raise ValueError("Gmail이 연동되어 있지 않습니다. 먼저 /gmail/login으로 연동해주세요.")

    creds = Credentials(
        token=credential.access_token,
        refresh_token=credential.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )

    if credential.token_expiry <= datetime.now(timezone.utc):
        creds.refresh(Request())
        expiry = creds.expiry
        credential.access_token = creds.token
        credential.token_expiry = expiry.replace(tzinfo=timezone.utc) if expiry.tzinfo is None else expiry
        db.commit()

    return build("gmail", "v1", credentials=creds)


def create_draft(user_id: int, db: Session, to: str | None, subject: str, body: str) -> str:
    service = _get_gmail_client(user_id, db)

    message = MIMEText(body)
    if to:
        message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    draft = service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft["id"]
