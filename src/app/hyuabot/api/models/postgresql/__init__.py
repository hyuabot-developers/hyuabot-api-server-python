from typing import TypeAlias

from sqlalchemy import Table, MetaData
from sqlalchemy.orm import declarative_base

ModelMeta: TypeAlias = declarative_base()


class BaseModel(ModelMeta):
    __abstract__ = True

    __table__: Table
    metadata: MetaData
