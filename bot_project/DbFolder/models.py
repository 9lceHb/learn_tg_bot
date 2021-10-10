from sqlalchemy import Column, Integer, String
from bot_project.DbFolder.db import Base, engine


class Applicant(Base):
    __tablename__ = 'applicants'
    #id = Column(Integer, primary_key=True)
    tg_id = Column(Integer(), primary_key=True)
    # name = Column(String())
    # age = Column(Integer())
    # expirience = Column(Integer())
    # komment = Column(String(240))
    # location = Column(String(240))

    def __repr__(self):
        return f'Applicant {self.tg_id}'#, {self.name}'


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
