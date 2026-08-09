import os

from anthropic import Anthropic
from dotenv import load_dotenv

from .tools import TOOL_DESCRIPTIONS

load_dotenv()

_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PLAN_TOOL = {
    "name": "record_plan",
    "description": "실행할 도구 목록을 순서대로 기록합니다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(TOOL_DESCRIPTIONS.keys()),
                },
                "description": "실행할 도구 이름을 순서대로 나열한 배열",
            },
        },
        "required": ["steps"],
    },
}


def create_plan(request: str) -> list[str]:
    tool_list = "\n".join(f"- {name}: {desc}" for name, desc in TOOL_DESCRIPTIONS.items())

    prompt = (
        "사용자 요청을 처리하기 위해 아래 도구들 중 필요한 것을 순서대로 골라 계획을 세우세요.\n\n"
        f"[사용 가능한 도구]\n{tool_list}\n\n"
        f"[사용자 요청]\n{request}\n\n"
        "record_plan 도구를 호출해서 실행 순서를 반환하세요."
    )

    response = _client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        tools=[PLAN_TOOL],
        tool_choice={"type": "tool", "name": "record_plan"},
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input["steps"]

    raise RuntimeError("Claude가 계획을 반환하지 않았습니다.")
