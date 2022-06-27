from sqlalchemy import Table, MetaData
from sqlalchemy.orm import DeclarativeMeta


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True

    __table__: Table
    metadata: MetaData
