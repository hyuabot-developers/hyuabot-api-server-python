from typing import Any

from sqlalchemy import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base

ModelMeta: Any = declarative_base()


class BaseModel(ModelMeta):
    __abstract__ = True

    __table__: Table
    metadata: MetaData
