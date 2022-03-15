# Query params
from fastapi import Query

campus_query = Query(None, alias="campus", description="캠퍼스 ID(seoul/erica)",
                     regex="^(seoul|erica)$", example="seoul")
restaurant_query = Query(None, alias="restaurant", description="식당 ID",
                         example="student_erica")
