from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class TeamBuildingRequest(BaseModel):
    city: str = Field(min_length=2, max_length=40)
    event_date: date
    participants: int = Field(ge=5, le=500)
    budget: int = Field(ge=1_000, le=1_000_000, description="总预算，单位：元")
    preference: Literal["balanced", "comfort", "economy"] = "balanced"


class Venue(BaseModel):
    id: str
    name: str
    capacity: int
    price: int
    comfort_score: float


class Catering(BaseModel):
    id: str
    name: str
    price_per_person: int
    quality_score: float


class Transport(BaseModel):
    id: str
    name: str
    price_per_person: int
    comfort_score: float


class Activity(BaseModel):
    id: str
    name: str
    price_per_person: int
    engagement_score: float


class BudgetBreakdown(BaseModel):
    venue: int
    catering: int
    transport: int
    activities: int
    total: int
    budget: int
    remaining: int


class TeamBuildingPlan(BaseModel):
    request_id: str
    status: Literal["success", "budget_unmet"]
    city: str
    venue: Venue
    catering: Catering
    transport: Transport
    activities: list[Activity]
    budget_breakdown: BudgetBreakdown
    plan_summary: str
    replan_count: int
    minimum_available_budget: int | None = None
    adjustment_suggestions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
