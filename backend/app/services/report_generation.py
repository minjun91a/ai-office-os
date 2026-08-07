import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MAX_TEXT_LENGTH = 100_000

REPORT_TYPE_INSTRUCTIONS = {
    "markdown_report": "문서 내용을 바탕으로 핵심을 정리한 Markdown 보고서를 작성하세요. 개요, 주요 내용, 결론 섹션으로 구성하세요.",
    "meeting_minutes": "문서 내용을 바탕으로 회의록 형식으로 작성하세요. 안건, 논의 내용, 결정 사항, 액션 아이템 섹션으로 구성하세요.",
    "work_report": "문서 내용을 바탕으로 업무 보고서를 작성하세요. 진행 상황, 이슈, 다음 계획 섹션으로 구성하세요.",
    "ppt_outline": "문서 내용을 바탕으로 발표용 PPT 슬라이드 구조를 작성하세요. 슬라이드마다 '## 슬라이드 N: 제목' 형식의 헤딩과 그 아래 핵심 bullet 3~5개로 구성하세요.",
    "word_outline": "문서 내용을 바탕으로 Word 문서용 목차/섹션 구조를 작성하세요. 각 섹션 제목과 섹션별 핵심 내용 요약으로 구성하세요.",
}


def generate_report(text: str, report_type: str, instructions: str | None = None) -> dict:
    truncated_text = text[:MAX_TEXT_LENGTH]
    type_instruction = REPORT_TYPE_INSTRUCTIONS.get(report_type)
    if type_instruction is None:
        raise ValueError(f"지원하지 않는 보고서 타입입니다: {report_type}")

    extra = f"\n\n추가 요청사항: {instructions}" if instructions else ""

    prompt = (
        f"{type_instruction}{extra}\n\n"
        "결과는 Markdown 형식으로만 작성하고, 첫 줄은 반드시 '# 제목' 형태의 "
        "레벨 1 헤딩으로 시작하세요. 다른 설명 문장 없이 Markdown 본문만 출력하세요.\n\n"
        f"[문서 내용]\n{truncated_text}"
    )

    response = _client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    content = None
    for block in response.content:
        if block.type == "text":
            content = block.text.strip()
            break

    if content is None:
        raise RuntimeError("Claude가 텍스트 응답을 반환하지 않았습니다.")

    first_line = content.splitlines()[0] if content else ""
    title = first_line.lstrip("#").strip() or report_type

    return {"title": title, "content": content}
