import os
from sqlalchemy import MetaData, create_engine

meta = MetaData()

host = 'mysql-db' # MySQL service/container name
database = os.environ.get('MYSQL_DATABASE')
username = os.environ.get('MYSQL_USERNAME')
password = os.environ.get('MYSQL_PASSWORD')

engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:3306/{database}')

conn = engine.connect()
