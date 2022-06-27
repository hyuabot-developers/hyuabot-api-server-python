from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql import sqltypes

from app.hyuabot.api.models.postgresql import BaseModel


class Cafeteria(BaseModel):
    __tablename__ = 'cafeteria'
    cafeteria_id = Column(sqltypes.String, primary_key=True)
    campus_id = Column(sqltypes.Integer, ForeignKey('campus.campus_id'))
    cafeteria_name = Column(sqltypes.String)


class Menu(BaseModel):
    __tablename__ = 'menu'
    __table_args__ = (
        PrimaryKeyConstraint('cafeteria_id', 'time_type', 'menu_description'),
    )
    cafeteria_id = Column(sqltypes.String, ForeignKey('cafeteria.cafeteria_id'))
    time_type = Column(sqltypes.String)
    menu_description = Column(sqltypes.String)
    menu_price = Column(sqltypes.String)
