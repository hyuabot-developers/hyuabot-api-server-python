from sqlalchemy import Table, MetaData
from sqlalchemy.orm import declarative_base

ModelMeta = declarative_base()  # type: ignore


class BaseModel(ModelMeta):
    __abstract__ = True

    __table__: Table
    metadata: MetaData
