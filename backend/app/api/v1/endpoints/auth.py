from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.worker import Worker
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user (Customer, Worker, Cooperative Admin, or Supervisor).
    Automatically creates associated profile (Customer or Worker) if applicable.
    """
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=user_in.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Automatically initialize Customer profile for customer role
    if user.role == UserRole.CUSTOMER:
        customer = Customer(
            user_id=user.id,
            name=user.full_name,
            phone=user.phone or "",
            email=user.email,
            city="Delhi",
            latitude=28.6139,
            longitude=77.2090
        )
        db.add(customer)
        db.commit()

    return user


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user and returns JWT bearer token along with role details.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value,
        "full_name": user.full_name,
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns current authenticated user details, including linked worker or customer profile.
    """
    data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }

    if current_user.role == UserRole.WORKER and current_user.worker_profile:
        wp = current_user.worker_profile
        data["worker_profile"] = {
            "worker_id": wp.id,
            "cooperative_id": wp.cooperative_id,
            "skills": wp.skills,
            "rating": wp.rating,
            "availability_status": wp.availability_status,
            "total_earnings": wp.total_earnings,
            "welfare_balance": wp.welfare_balance,
        }
    elif current_user.role == UserRole.CUSTOMER and current_user.customer_profile:
        cp = current_user.customer_profile
        data["customer_profile"] = {
            "customer_id": cp.id,
            "city": cp.city,
            "address": cp.address,
            "latitude": cp.latitude,
            "longitude": cp.longitude,
        }

    return data
