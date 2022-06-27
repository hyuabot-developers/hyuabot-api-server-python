from pydantic import BaseModel, Field


class ReadingRoomItem(BaseModel):
    name: str = Field(alias="name", title="열람실 이름", description="예시: 제1열람실")
    is_active: bool = Field(alias="isActive", title="열람실 개방 여부", description="예시: True")
    is_reservable: bool = Field(alias="isReservable", title="예약 가능 여부", description="예시: True")
    total: int = Field(alias="total", title="열람실 총 좌석 수", description="예시: 100")
    active_total: int = Field(alias="activeTotal", title="열람실 사용 가능 좌석 수", description="예시: 50")
    occupied: int = Field(alias="occupied", title="열람실 사용중 좌석 수", description="예시: 50")
    available: int = Field(alias="available", title="열람실 예약 가능 좌석 수", description="예시: 50")
