from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.students import Student
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("20/minute")
def register(
    request: Request,
    credentials: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user and return a token."""
    existing = db.query(Student).filter(Student.email == credentials.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = Student(
        name=credentials.name,
        email=credentials.email,
        hashed_password=hash_password(credentials.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    """Log in and receive an access token."""
    user = db.query(Student).filter(Student.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}