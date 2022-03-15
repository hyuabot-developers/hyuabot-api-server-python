from fastapi import Query

from app.hyuabot.api.schemas.shuttle import ShuttleStop

shuttle_line_type = ["DH", "DY", "C"]
shuttle_stop_type = ["Dormitory", "Shuttlecock_O", "Station", "Terminal", "Shuttlecock_I"]

# 셔틀버스 정류장
shuttle_dormitory = ShuttleStop(
    koreanName="기숙사",
    englishName="Dormitory",
    latitude=37.29339607529377,
    longitude=126.83630604103446,
)
shuttle_shuttlecock_o = ShuttleStop(
    koreanName="셔틀콕",
    englishName="Shuttlecock",
    latitude=37.29875417910844,
    longitude=126.83784054072336,
)
shuttle_station = ShuttleStop(
    koreanName="한대앞역",
    englishName="Hanyang University at Ansan Station",
    latitude=37.308494476826155,
    longitude=126.85310236423418,
)
shuttle_terminal = ShuttleStop(
    koreanName="예술인",
    englishName="Ansan Terminal",
    latitude=37.31945164682341,
    longitude=126.8455453372041,
)
shuttle_shuttlecock_i = ShuttleStop(
    koreanName="셔틀콕 건너편",
    englishName="Opposite of Shuttlecock",
    latitude=37.29869328231496,
    longitude=126.8377767466817,
)

latitude_query = Query(None, alias="latitude", description="위도", example="37.29246290291605")
longitude_query = Query(None, alias="longitude", description="경도", example="126.8359786509412")
