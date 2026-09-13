import uuid

from .config import get_settings
from .decision import LLMDecisionEngine, RuleDecisionEngine
from .graph import create_planner_graph
from .schemas import TeamBuildingPlan, TeamBuildingRequest


class TeamBuildingPlannerService:
    def __init__(self):
        settings = get_settings()
        settings.require_llm_credentials()
        engine = RuleDecisionEngine() if settings.planner_mode == "rule" else LLMDecisionEngine(settings.openai_api_key or "", settings.openai_base_url, settings.openai_model)
        self.graph = create_planner_graph(engine=engine)

    def plan(self, request: TeamBuildingRequest, request_id: str | None = None) -> TeamBuildingPlan:
        state = self.graph.invoke({"request": request, "replan_count": 0, "warnings": []})
        return TeamBuildingPlan(request_id=request_id or str(uuid.uuid4()), city=request.city, venue=state["venue"], catering=state["catering"], transport=state["transport"], activities=state["activities"], budget_breakdown=state["breakdown"], plan_summary=f"{request.city} {request.participants} 人团建：{state['venue'].name}、{state['catering'].name}、{state['transport'].name}，活动为{'、'.join(item.name for item in state['activities'])}。", status=state["status"], replan_count=state.get("replan_count", 0), minimum_available_budget=state.get("minimum_available_budget"), adjustment_suggestions=state.get("adjustment_suggestions", []), warnings=list(dict.fromkeys(state.get("warnings", []))))
