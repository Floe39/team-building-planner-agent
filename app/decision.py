import json
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from openai import OpenAI

from .schemas import Activity, Catering, TeamBuildingRequest, Transport, Venue

T = TypeVar("T", Venue, Catering, Transport, Activity)


@dataclass
class DecisionOutcome(Generic[T]):
    value: T | list[Activity]
    fallback_reason: str | None = None


class DecisionEngine(Protocol):
    def choose_one(self, candidates: list[T], request: TeamBuildingRequest) -> DecisionOutcome[T]: ...

    def choose_activities(self, candidates: list[Activity], request: TeamBuildingRequest) -> DecisionOutcome[Activity]: ...


class RuleDecisionEngine:
    def choose_one(self, candidates: list[T], request: TeamBuildingRequest) -> DecisionOutcome[T]:
        if request.preference == "economy":
            return DecisionOutcome(min(candidates, key=self._price))
        if request.preference == "comfort":
            return DecisionOutcome(max(candidates, key=self._score))
        return DecisionOutcome(sorted(candidates, key=lambda item: (self._price(item), -self._score(item)))[len(candidates) // 2])

    def choose_activities(self, candidates: list[Activity], request: TeamBuildingRequest) -> DecisionOutcome[Activity]:
        ranked = sorted(candidates, key=lambda item: item.price_per_person)
        return DecisionOutcome(ranked[:1] if request.preference == "economy" else [ranked[0], ranked[1]])

    @staticmethod
    def _price(item: T) -> int:
        return item.price if isinstance(item, Venue) else item.price_per_person

    @staticmethod
    def _score(item: T) -> float:
        if isinstance(item, Catering):
            return item.quality_score
        return item.comfort_score if not isinstance(item, Activity) else item.engagement_score


class LLMDecisionEngine(RuleDecisionEngine):
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def choose_one(self, candidates: list[T], request: TeamBuildingRequest) -> DecisionOutcome[T]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "只输出 JSON：{\"id\": \"候选 id\"}"}, {"role": "user", "content": json.dumps({"preference": request.preference, "candidates": [item.model_dump() for item in candidates]}, ensure_ascii=False)}],
                response_format={"type": "json_object"}, temperature=0,
            )
            selected_id = json.loads(response.choices[0].message.content or "{}").get("id")
            selected = next((item for item in candidates if item.id == selected_id), None)
            if selected:
                return DecisionOutcome(selected)
            raise ValueError("LLM returned an unknown candidate")
        except Exception:
            result = super().choose_one(candidates, request)
            result.fallback_reason = "LLM 选择失败，已回退至规则引擎。"
            return result
