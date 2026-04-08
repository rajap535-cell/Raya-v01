from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)

    age = Column(Integer)
    gender = Column(String)
    height_cm = Column(Integer)
    baseline_activity_type = Column(String)