from sqlalchemy import Column, Integer, String
from db import Base, engine

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String())
    salary = Column(Integer())
    email = Column(String(120), unique=True)

    def __repr__(self) -> str:
        return f'User {self.id}, {self.name}'

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine) 