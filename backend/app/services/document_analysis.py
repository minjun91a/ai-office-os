import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MAX_TEXT_LENGTH = 100_000

ANALYSIS_TOOL = {
    "name": "record_document_analysis",
    "description": "문서 분석 결과를 구조화된 형태로 기록합니다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "문서 전체 핵심 내용 요약 (3~5문장)",
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "문서를 대표하는 핵심 키워드 5~10개",
            },
            "action_items": {
                "type": "array",
                "items": {"type": "string"},
                "description": "문서에서 도출되는 실행해야 할 작업 목록. 없으면 빈 배열",
            },
            "assignees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "문서에서 언급된 담당자 이름 또는 역할. 없으면 빈 배열",
            },
            "deadlines": {
                "type": "array",
                "items": {"type": "string"},
                "description": "문서에서 언급된 마감일 또는 일정. 없으면 빈 배열",
            },
            "importance": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "문서의 업무 중요도",
            },
            "is_meeting_minutes": {
                "type": "boolean",
                "description": "이 문서가 회의록인지 여부",
            },
            "meeting_summary": {
                "type": "string",
                "description": "회의록인 경우 논의 안건과 결정 사항 요약. 회의록이 아니면 빈 문자열",
            },
        },
        "required": [
            "summary",
            "keywords",
            "action_items",
            "assignees",
            "deadlines",
            "importance",
            "is_meeting_minutes",
            "meeting_summary",
        ],
    },
}


def analyze_document(text: str) -> dict:
    truncated_text = text[:MAX_TEXT_LENGTH]

    response = _client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2048,
        tools=[ANALYSIS_TOOL],
        tool_choice={"type": "tool", "name": "record_document_analysis"},
        messages=[
            {
                "role": "user",
                "content": (
                    "다음은 업무용으로 업로드된 문서의 전체 내용입니다. "
                    "이 문서를 분석해서 record_document_analysis 도구를 호출하세요.\n\n"
                    f"[문서 내용]\n{truncated_text}"
                ),
            }
        ],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input

    raise RuntimeError("Claude가 분석 결과를 반환하지 않았습니다.")