from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


engine = create_engine('postgresql://uuucnrgc:I-H2O5tFjxjOciBWvojaJNBmpkd7-H1r@hattie.db.elephantsql.com/uuucnrgc')
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()