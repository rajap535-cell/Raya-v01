from app.database import engine, Base

# Import ALL models explicitly
from app.models.user import User
from app.models.daily_log import DailyLog
from app.models.prediction import EnergyPrediction

# Create tables
Base.metadata.create_all(bind=engine)

print("Database created successfully!")