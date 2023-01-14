from sqlalchemy import Table, Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from app.config.database import meta, engine

vehicles = Table(
    'vehicles', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255)),
    Column('capacity', Integer),
    Column('model_id', Integer, ForeignKey('models.id'))
)

vehicles.create(engine, checkfirst=True)
