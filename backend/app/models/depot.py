from sqlalchemy import Table, Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Float, Integer, String
from app.config.database import meta, engine

depots = Table(
    'depots', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255)),
    Column('latitude', Float),
    Column('longitude', Float),
    Column('address', String(255)),
    Column('model_id', Integer, ForeignKey('models.id'), unique=True)
)

depots.create(engine, checkfirst=True)
