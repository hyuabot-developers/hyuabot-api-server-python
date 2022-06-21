from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql import sqltypes

from app.hyuabot.api.models.postgresql import BaseModel


class Cafeteria(BaseModel):
    __tablename__ = 'cafeteria'
    cafeteria_id = Column(sqltypes.String, primary_key=True)
    campus_id = Column(sqltypes.Integer, ForeignKey('campus.campus_id'))
    cafeteria_name = Column(sqltypes.String)


class Menu(BaseModel):
    __tablename__ = 'menu'
    cafeteria_id = Column(sqltypes.String, ForeignKey('cafeteria.cafeteria_id'), primary_key=True)
    time_type = Column(sqltypes.String)
    menu_description = Column(sqltypes.String)
    menu_price = Column(sqltypes.String)
