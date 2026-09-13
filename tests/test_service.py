from datetime import date

from app.schemas import TeamBuildingRequest
from app.service import TeamBuildingPlannerService


def request(**overrides) -> TeamBuildingRequest:
    data = {"city": "上海", "event_date": date(2026, 10, 1), "participants": 20, "budget": 20_000, "preference": "comfort"}
    data.update(overrides)
    return TeamBuildingRequest(**data)


def test_returns_feasible_plan():
    result = TeamBuildingPlannerService().plan(request())
    assert result.status == "success"
    assert result.budget_breakdown.total <= result.budget_breakdown.budget


def test_replans_before_declaring_budget_unmet():
    result = TeamBuildingPlannerService().plan(request(budget=4_000))
    assert result.status == "budget_unmet"
    assert result.replan_count == 1
    assert result.minimum_available_budget == result.budget_breakdown.total
