#  SQLAlchemy 테이블 객체를 사용한 명시적 ORM 매핑
from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import mapper
from models import OrderLine


metadata = MetaData()

order_lines = Table(
    'order_lines', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(250)),
    Column('qty', Integer, nullable=False),
    Column('orderid', String(255))
)


def start_mappers():
    lines_mapper = mapper(OrderLine, order_lines)
