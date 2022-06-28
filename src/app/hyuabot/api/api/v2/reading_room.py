import strawberry


@strawberry.type
class ReadingRoomItem:
    room_name: str
    campus_id: int
    is_active: bool
    is_reservable: bool
    total_seat: int
    active_seat: int
    occupied_seat: int
    available_seat: int

