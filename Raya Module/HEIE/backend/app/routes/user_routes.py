from fastapi import APIRouter
from app.database import SessionLocal
from app.models.user import User

router = APIRouter()

@router.post("/create_user")
def create_user(
    name: str,
    email: str,
    age: int,
    gender: str,
    height_cm: int
):
    db = SessionLocal()

    user = User(
        name=name,
        email=email,
        age=age,
        gender=gender,
        height_cm=height_cm,
        baseline_activity_type="moderate"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }