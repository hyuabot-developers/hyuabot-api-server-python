from sqlalchemy import Table, MetaData
from sqlalchemy.orm import declarative_base
# type: ignore
ModelMeta = declarative_base()


class BaseModel(ModelMeta):
    __abstract__ = True

    __table__: Table
    metadata: MetaData
