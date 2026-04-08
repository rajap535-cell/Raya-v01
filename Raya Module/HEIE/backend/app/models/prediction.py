from sqlalchemy import Column, Integer, Float, ForeignKey, String
from app.database import Base

class EnergyPrediction(Base):
    __tablename__ = "energy_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    date = Column(String)
    predicted_calories = Column(Float)
    baseline_calories = Column(Float)
    adjusted_calories = Column(Float)