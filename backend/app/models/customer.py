from sqlalchemy import Table, Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Float, Integer, String
from app.config.database import meta, engine

customers = Table(
    'customers', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255)),
    Column('demand', Integer),
    Column('latitude', Float),
    Column('longitude', Float),
    Column('address', String(255)),
    Column('model_id', Integer, ForeignKey('models.id'))
)

customers.create(engine, checkfirst=True)
