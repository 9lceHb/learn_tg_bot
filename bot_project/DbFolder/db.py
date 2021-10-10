
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
#url = 'sqlite:///server.db'
url = 'postgresql://uuucnrgc:I-H2O5tFjxjOciBWvojaJNBmpkd7-H1r@hattie.db.elephantsql.com:5432/uuucnrgc'
engine = create_engine(url)

db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
