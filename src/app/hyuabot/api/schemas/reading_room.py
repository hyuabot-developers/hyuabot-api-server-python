from pydantic.main import BaseModel


class ReadingRoomItem(BaseModel):
    name: str
    isActive: bool
    isReservable: bool
    total: int
    activeTotal: int
    occupied: int
    available: int
