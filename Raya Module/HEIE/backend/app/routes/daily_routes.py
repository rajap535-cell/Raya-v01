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
        energy_feeling=energy_feeling
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

    total_steps = db.query(func.sum(DailyLog.steps))\
        .filter(DailyLog.user_id == user_id).scalar()

    avg_screen = db.query(func.avg(DailyLog.screen_time))\
        .filter(DailyLog.user_id == user_id).scalar()

    avg_work = db.query(func.avg(DailyLog.work_hours))\
        .filter(DailyLog.user_id == user_id).scalar()

    # 🔹 STEP 3: STRUCTURE ANALYTICS
    analytics_data = {
        "avg_sleep": avg_sleep,
        "total_steps": total_steps,
        "avg_screen_time": avg_screen,
        "avg_work_hours": avg_work
    }

    # 🔹 STEP 4: COMPARISON ENGINE (CORE INTELLIGENCE)
    insights = compare_user(user, analytics_data)

    # 🔹 STEP 5: FINAL RESPONSE
    return {
        "analytics": analytics_data,
        "insights": insights
    }