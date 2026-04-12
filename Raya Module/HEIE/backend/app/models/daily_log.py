from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date
from app.database import Base

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)

    # 🔗 Relation
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 📅 Core tracking
    date = Column(Date, nullable=False)

    # 🧍 Body metrics
    weight_kg = Column(Float, nullable=True)

    # 🧠 Lifestyle
    activity_level = Column(String, nullable=True)

    # 📊 Daily stats
    steps = Column(Integer, nullable=False)
    sleep_hours = Column(Float, nullable=False)
    work_hours = Column(Float, nullable=False)      # ✅ Float (not Integer)
    screen_time = Column(Float, nullable=False)     # ✅ FIXED

    # 🍽️ Nutrition
    calories_intake = Column(Integer, nullable=True)

    # ⚡ Subjective
    energy_feeling = Column(String, nullable=True)