import os
from datetime import timezone

from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session

from app.models.google_credential import GoogleCredential

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [GOOGLE_REDIRECT_URI],
    }
}


def build_authorization_url(state: str) -> str:
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI,
        autogenerate_code_verifier=False,
    )
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        state=state,
    )
    return authorization_url


def exchange_code_and_save(code: str, user_id: int, db: Session) -> GoogleCredential:
    flow = Flow.from_client_config(
        CLIENT_CONFIG, 
        scopes=SCOPES, 
        redirect_uri=GOOGLE_REDIRECT_URI,
        autogenerate_code_verifier=False,
    )
    flow.fetch_token(code=code)
    creds = flow.credentials

    expiry = creds.expiry
    if expiry is not None and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    credential = (
        db.query(GoogleCredential).filter(GoogleCredential.user_id == user_id).first()
    )
    if credential is None:
        if not creds.refresh_token:
            raise ValueError(
                "Google이 refresh_token을 반환하지 않았습니다. 동의 화면에서 다시 승인해주세요."
            )
        credential = GoogleCredential(
            user_id=user_id, refresh_token=creds.refresh_token
        )
        db.add(credential)
    elif creds.refresh_token:
        credential.refresh_token = creds.refresh_token

    credential.access_token = creds.token
    credential.token_expiry = expiry

    db.commit()
    db.refresh(credential)
    return credential
