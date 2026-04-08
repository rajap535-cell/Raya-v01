from sqlalchemy import Column, Integer, Float, String, ForeignKey
from app.database import Base

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    date = Column(String)
    weight_kg = Column(Float)
    activity_level = Column(String)
    steps = Column(Integer)

    sleep_hours = Column(Float)
    calories_intake = Column(Integer)

    energy_feeling = Column(String)