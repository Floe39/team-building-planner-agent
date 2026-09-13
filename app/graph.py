from operator import add
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from .decision import DecisionEngine, RuleDecisionEngine
from .schemas import Activity, BudgetBreakdown, Catering, TeamBuildingRequest, Transport, Venue
from .tools import MockTeamBuildingDataProvider


class PlannerState(TypedDict, total=False):
    request: TeamBuildingRequest
    venue: Venue
    catering: Catering
    transport: Transport
    activities: list[Activity]
    breakdown: BudgetBreakdown
    replan_count: int
    warnings: Annotated[list[str], add]
    status: Literal["success", "budget_unmet"]
    minimum_available_budget: int | None
    adjustment_suggestions: list[str]


def create_planner_graph(provider: MockTeamBuildingDataProvider | None = None, engine: DecisionEngine | None = None):
    provider, engine = provider or MockTeamBuildingDataProvider(), engine or RuleDecisionEngine()

    def select(state: PlannerState) -> dict:
        request = state["request"]
        venue = engine.choose_one([item for item in provider.venues(request) if item.capacity >= request.participants], request)
        catering = engine.choose_one(provider.catering(request), request)
        transport = engine.choose_one(provider.transport(request), request)
        activities = engine.choose_activities(provider.activities(request), request)
        warnings = [reason for reason in [venue.fallback_reason, catering.fallback_reason, transport.fallback_reason, activities.fallback_reason] if reason]
        return {"venue": venue.value, "catering": catering.value, "transport": transport.value, "activities": activities.value, "warnings": warnings}

    def calculate(state: PlannerState) -> dict:
        request = state["request"]
        venue, catering, transport, activities = state["venue"], state["catering"], state["transport"], state["activities"]
        catering_total = catering.price_per_person * request.participants
        transport_total = transport.price_per_person * request.participants
        activity_total = sum(item.price_per_person for item in activities) * request.participants
        total = venue.price + catering_total + transport_total + activity_total
        return {"breakdown": BudgetBreakdown(venue=venue.price, catering=catering_total, transport=transport_total, activities=activity_total, total=total, budget=request.budget, remaining=request.budget - total)}

    def next_step(state: PlannerState) -> str:
        if state["breakdown"].total <= state["request"].budget:
            return "compose"
        return "replan" if state.get("replan_count", 0) == 0 else "compose"

    def replan(state: PlannerState) -> dict:
        request = state["request"]
        venue = min((item for item in provider.venues(request) if item.capacity >= request.participants), key=lambda item: item.price)
        catering = min(provider.catering(request), key=lambda item: item.price_per_person)
        transport = min(provider.transport(request), key=lambda item: item.price_per_person)
        activities = [min(provider.activities(request), key=lambda item: item.price_per_person)]
        return {"venue": venue, "catering": catering, "transport": transport, "activities": activities, "replan_count": 1, "warnings": ["初始方案超预算，已切换为经济型供应商与单项活动。"]}

    def compose(state: PlannerState) -> dict:
        breakdown, request = state["breakdown"], state["request"]
        feasible = breakdown.total <= request.budget
        return {"status": "success" if feasible else "budget_unmet", "minimum_available_budget": None if feasible else breakdown.total, "adjustment_suggestions": [] if feasible else ["增加预算", "减少参与人数", "缩短活动或取消接驳"], "warnings": [] if feasible else ["已采用最低成本组合，预算仍不足。"]}

    graph = StateGraph(PlannerState)
    graph.add_node("select", select); graph.add_node("calculate", calculate); graph.add_node("replan", replan); graph.add_node("compose", compose)
    graph.add_edge(START, "select"); graph.add_edge("select", "calculate"); graph.add_conditional_edges("calculate", next_step, {"replan": "replan", "compose": "compose"}); graph.add_edge("replan", "calculate"); graph.add_edge("compose", END)
    return graph.compile()
