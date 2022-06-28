import strawberry

from app.hyuabot.api.api.v2.shuttle import Shuttle


@strawberry.type
class Query:
    @strawberry.field
    def shuttle(self) -> Shuttle:
        return Shuttle()
