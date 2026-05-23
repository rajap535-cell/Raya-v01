from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import SessionLocal
from app.models.daily_log import DailyLog
from app.models.user import User
from app.core.comparator import compare_user

router = APIRouter()

# -----------------------------
# DB Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# CREATE DAILY LOG
# -----------------------------
@router.post("/log_daily")
def log_daily(
    user_id: int,
    steps: int,
    sleep_hours: float,
    work_hours: float,
    screen_time: float,
    weight_kg: float = None,
    activity_level: str = None,
    calories_intake: int = None,
    energy_feeling: str = None,
    exercise_minutes: int = None,
    learning_hours: float = None,
    water_intake: float = None,
    stress_level: str = None,
    mood: str = None,

    db: Session = Depends(get_db)
):

    log = DailyLog(
        user_id=user_id,
        date=date.today(),

        steps=steps,
        sleep_hours=sleep_hours,
        work_hours=work_hours,
        screen_time=screen_time,

        weight_kg=weight_kg,
        activity_level=activity_level,
        calories_intake=calories_intake,
        energy_feeling=energy_feeling,
        exercise_minutes=exercise_minutes,
        learning_hours=learning_hours,
        water_intake=water_intake,
        stress_level=stress_level,
        mood=mood
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "message": "Daily log added successfully",
        "log_id": log.id
    }


# -----------------------------
# GET USER LOGS
# -----------------------------
@router.get("/logs/{user_id}")
def get_logs(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(DailyLog).filter(DailyLog.user_id == user_id).all()
    return logs


# -----------------------------
# ANALYTICS + INTELLIGENCE
# -----------------------------
@router.get("/analytics/{user_id}")
def get_analytics(user_id: int, db: Session = Depends(get_db)):

    # 🔹 STEP 1: FETCH USER
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": "User not found"}

    # 🔹 STEP 2: GET REAL DATA FROM DB
    avg_sleep = db.query(func.avg(DailyLog.sleep_hours))\
        .filter(DailyLog.user_id == user_id).scalar()

    avg_steps = db.query(func.avg(DailyLog.steps))\
        .filter(DailyLog.user_id == user_id).scalar()

    avg_screen = db.query(func.avg(DailyLog.screen_time))\
        .filter(DailyLog.user_id == user_id).scalar()

    avg_work = db.query(func.avg(DailyLog.work_hours))\
        .filter(DailyLog.user_id == user_id).scalar()

    avg_learning = db.query(func.avg(DailyLog.learning_hours))\
    .filter(DailyLog.user_id == user_id).scalar()

    avg_exercise = db.query(func.avg(DailyLog.exercise_minutes))\
        .filter(DailyLog.user_id == user_id).scalar()

    avg_water = db.query(func.avg(DailyLog.water_intake))\
        .filter(DailyLog.user_id == user_id).scalar()

    avg_calories = db.query(func.avg(DailyLog.calories_intake))\
        .filter(DailyLog.user_id == user_id).scalar()

    # 🔹 STEP 3: STRUCTURE ANALYTICS
    analytics_data = {
        "avg_sleep": avg_sleep,
        "avg_steps": avg_steps, 
        "avg_screen_time": avg_screen,
        "avg_work_hours": avg_work,
        "avg_learning": avg_learning,
        "avg_exercise": avg_exercise,
        "avg_water": avg_water,
        "avg_calories": avg_calories

    }

    # 🔹 STEP 4: COMPARISON ENGINE (CORE INTELLIGENCE)
    insights = compare_user(user, analytics_data)

    # 🔹 STEP 5: FINAL RESPONSE
    return {
        "analytics": analytics_data,
        "insights": insights
    }