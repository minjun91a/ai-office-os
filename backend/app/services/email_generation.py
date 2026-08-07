import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MAX_TEXT_LENGTH = 100_000

TONE_INSTRUCTIONS = {
    "polite": "정중하고 격식있는 존댓말 톤으로 작성하세요.",
    "concise": "핵심만 간결하게, 불필요한 인사말 없이 작성하세요.",
    "report": "상사·관리자에게 보고하는 형식의 톤으로 작성하세요.",
}

LANGUAGE_INSTRUCTIONS = {
    "ko": "한국어로 작성하세요.",
    "en": "영어(English)로 작성하세요.",
}

EMAIL_TOOL = {
    "name": "record_email_draft",
    "description": "이메일 초안(제목, 본문)을 구조화된 형태로 기록합니다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "subject": {"type": "string", "description": "이메일 제목"},
            "body": {"type": "string", "description": "이메일 본문 (인사말, 본문, 맺음말 포함)"},
        },
        "required": ["subject", "body"],
    },
}


def generate_email(text: str, tone: str, language: str, instructions: str | None = None) -> dict:
    truncated_text = text[:MAX_TEXT_LENGTH]
    tone_instruction = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["polite"])
    language_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["ko"])
    extra = f"\n\n추가 요청사항: {instructions}" if instructions else ""

    prompt = (
        "다음 문서 내용을 요약해서 이메일 초안을 작성하세요. "
        f"{tone_instruction} {language_instruction}{extra}\n\n"
        "record_email_draft 도구를 호출해서 제목과 본문을 반환하세요.\n\n"
        f"[문서 내용]\n{truncated_text}"
    )

    response = _client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2048,
        tools=[EMAIL_TOOL],
        tool_choice={"type": "tool", "name": "record_email_draft"},
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input

    raise RuntimeError("Claude가 이메일 초안을 반환하지 않았습니다.")
