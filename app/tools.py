from .schemas import Activity, Catering, TeamBuildingRequest, Transport, Venue


class MockTeamBuildingDataProvider:
    """本地模拟供应商目录；后续可替换为真实场地或活动 API。"""

    def venues(self, request: TeamBuildingRequest) -> list[Venue]:
        return [
            Venue(id="venue-comfort", name=f"{request.city}湖畔会议中心", capacity=120, price=8_000, comfort_score=4.9),
            Venue(id="venue-value", name=f"{request.city}创意园多功能厅", capacity=80, price=4_500, comfort_score=4.4),
            Venue(id="venue-budget", name=f"{request.city}社区活动空间", capacity=60, price=2_000, comfort_score=4.0),
        ]

    def catering(self, request: TeamBuildingRequest) -> list[Catering]:
        return [
            Catering(id="catering-comfort", name="主题自助餐", price_per_person=220, quality_score=4.9),
            Catering(id="catering-value", name="商务简餐", price_per_person=130, quality_score=4.4),
            Catering(id="catering-budget", name="轻食茶歇", price_per_person=70, quality_score=4.0),
        ]

    def transport(self, request: TeamBuildingRequest) -> list[Transport]:
        return [
            Transport(id="transport-comfort", name="专车接驳", price_per_person=120, comfort_score=4.9),
            Transport(id="transport-value", name="大巴往返", price_per_person=65, comfort_score=4.4),
            Transport(id="transport-budget", name="公共交通补贴", price_per_person=25, comfort_score=3.8),
        ]

    def activities(self, request: TeamBuildingRequest) -> list[Activity]:
        return [
            Activity(id="activity-workshop", name="协作工作坊", price_per_person=180, engagement_score=4.9),
            Activity(id="activity-outdoor", name="户外定向挑战", price_per_person=120, engagement_score=4.6),
            Activity(id="activity-game", name="破冰桌游", price_per_person=50, engagement_score=4.1),
        ]
