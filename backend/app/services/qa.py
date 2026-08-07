import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_answer(question: str, context_chunks: list[str]) -> str:
    if not context_chunks:
        return "관련된 문서 내용을 찾지 못했습니다."

    context = "\n\n---\n\n".join(context_chunks)
    prompt = (
        "아래는 사용자가 업로드한 문서에서 검색된 관련 내용입니다. "
        "이 내용만 근거로 질문에 답하세요. 문서에 없는 내용은 추측하지 말고 "
        "\"문서에서 관련 내용을 찾을 수 없습니다\"라고 답하세요.\n\n"
        f"[문서 내용]\n{context}\n\n"
        f"[질문]\n{question}"
    )

    response = _client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "text":
            return block.text

    return "답변을 생성하지 못했습니다."
