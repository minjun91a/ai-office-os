from sqlalchemy.orm import Session

from .state import AgentState
from .tools import TOOLS

MAX_RETRIES = 2


def make_execute_node(db: Session):
    def execute_node(state: AgentState) -> dict:
        plan = state["plan"]
        current_step = state["current_step"]

        if current_step >= len(plan):
            return {}

        tool_name = plan[current_step]
        tool_fn = TOOLS.get(tool_name)

        if tool_fn is None:
            return {
                "error": f"알 수 없는 도구입니다: {tool_name}",
                "logs": [f"[실패] {tool_name}: 존재하지 않는 도구"],
            }

        try:
            result = tool_fn(state, db)
            result["current_step"] = current_step + 1
            result["retry_count"] = 0
            result["error"] = None
            result["logs"] = [f"[성공] {tool_name} 실행 완료"]
            return result
        except Exception as exc:
            return {
                "error": str(exc),
                "retry_count": state.get("retry_count", 0) + 1,
                "logs": [f"[실패] {tool_name}: {exc}"],
            }

    return execute_node


def route_after_execute(state: AgentState) -> str:
    if state.get("error"):
        if state.get("retry_count", 0) < MAX_RETRIES:
            return "execute"
        return "fail"

    if state["current_step"] >= len(state["plan"]):
        return "finish"

    return "execute"


def finish_node(state: AgentState) -> dict:
    return {"logs": ["모든 단계 완료"]}


def fail_node(state: AgentState) -> dict:
    return {"logs": [f"최대 재시도 횟수 초과, 실패: {state.get('error')}"]}
