from sqlalchemy.orm import Session

from langgraph.graph import END, StateGraph

from .execute import fail_node, finish_node, make_execute_node, route_after_execute
from .plan import create_plan
from .state import AgentState


def plan_node(state: AgentState) -> dict:
    steps = create_plan(state["request"])
    return {
        "plan": steps,
        "current_step": 0,
        "logs": [f"계획 수립: {' → '.join(steps)}"],
    }


def build_agent_graph(db: Session):
    graph = StateGraph(AgentState)

    graph.add_node("plan", plan_node)
    graph.add_node("execute", make_execute_node(db))
    graph.add_node("finish", finish_node)
    graph.add_node("fail", fail_node)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "execute")
    graph.add_conditional_edges(
        "execute",
        route_after_execute,
        {"execute": "execute", "finish": "finish", "fail": "fail"},
    )
    graph.add_edge("finish", END)
    graph.add_edge("fail", END)

    return graph.compile()
