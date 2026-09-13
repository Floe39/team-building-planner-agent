from starlette.requests import Request

from app.main import create_plan, health
from app.schemas import TeamBuildingRequest


def fake_request() -> Request:
    return Request({"type": "http", "method": "POST", "path": "/api/team-buildings/plan", "headers": [(b"x-request-id", b"test-request-id")]})


def test_health_endpoint():
    assert health() == {"status": "ok"}


def test_plan_endpoint():
    payload = TeamBuildingRequest(city="上海", event_date="2026-10-01", participants=20, budget=4_000, preference="economy")
    response = create_plan(payload, fake_request())
    assert response.request_id == "test-request-id"
    assert response.status == "budget_unmet"
