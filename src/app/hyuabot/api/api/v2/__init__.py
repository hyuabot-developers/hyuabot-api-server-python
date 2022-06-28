import strawberry

from app.hyuabot.api.api.v2.shuttle import Shuttle
from app.hyuabot.api.api.v2.subway import Subway


@strawberry.type
class Query:
    @strawberry.field
    def shuttle(self) -> Shuttle:
        return Shuttle()

    @strawberry.field
    def subway(self) -> Subway:
        return Subway()
