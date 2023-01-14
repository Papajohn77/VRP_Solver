from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from app.config.database import meta, engine

models = Table(
    'models', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), unique=True)
)

models.create(engine, checkfirst=True)
