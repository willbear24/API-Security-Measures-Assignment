from fastapi import APIRouter, Depends, HTTPException, Query, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.database import get_db
from app.models.students import Student
from app.schemas.students import (
    StudentCreate,
    StudentUpdate,
    StudentPatch,
    StudentResponse,
)
from app.utils.security import get_current_user
from app.utils.notifcations import send_notification, log_activity
from app.limiter import limiter

router = APIRouter(prefix="/students", tags=["Students"])


def get_student_or_404(db: Session, student_id: int) -> Student:
    """Helper: fetch a student or raise 404"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


# CREATE
@router.post(
    "/",
    response_model=StudentResponse,
    status_code=201,
    responses={
        422: {"description": "Validation error"},
        401: {"description": "Not authenticated"},
    },
    summary="Create a new student",
)
@limiter.limit("20/minute")
def create_student(
    request: Request,
    student: StudentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new student.

    - Requires an authenticated user.
    - Sends a welcome notification and records the activity in the background.
    - Returns `409` when the email address is already registered.
    """
    db_student = Student(**student.model_dump())

    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Student with this email already exists.",
        )

    background_tasks.add_task(
        send_notification,
        email=db_student.email,
        message=f"Hi {db_student.name}, welcome to our platform!",
    )

    background_tasks.add_task(
        log_activity,
        user_id=db_student.id,
        action="Student Created",
    )

    return db_student


# READ (many)
@router.get(
    "/",
    response_model=list[StudentResponse],
    responses={
        422: {"description": "Invalid filter or pagination parameter"},
    },
    summary="List all students",
)
@limiter.limit("60/minute")
def list_students(
    request: Request,
    name: Optional[str] = Query(default=None, max_length=100),
    email: Optional[str] = Query(default=None, max_length=200),
    grade_level: Optional[int] = Query(default=None, ge=1, le=12),
    is_enrolled: Optional[bool] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List students with optional filters and pagination.

    - Filters by name, email, grade level, and enrollment status when provided.
    - Uses `skip` and `limit` for pagination.
    - Returns a list of student records.
    """
    # SQLAlchemy's .filter()/.ilike() bind user input as query parameters instead of
    # interpolating it into the SQL string, so the database always treats it as data,
    # never executable SQL. This prevents SQL injection.
    #
    # Vulnerable (string interpolation lets an attacker close the quote and inject SQL):
    #   query = db.execute(f"SELECT * FROM students WHERE name LIKE '%{name}%'")
    #   # name = "%'; DROP TABLE students; --" would execute arbitrary SQL.
    #
    # Safe (parameterized, used below):
    #   query = query.filter(Student.name.ilike(f"%{name}%"))
    #   # `name` is passed as a bound parameter, not concatenated into the SQL text.
    query = db.query(Student)

    if name is not None:
        query = query.filter(Student.name.ilike(f"%{name}%"))
    if email is not None:
        query = query.filter(Student.email.ilike(f"%{email}%"))
    if grade_level is not None:
        query = query.filter(Student.grade_level == grade_level)
    if is_enrolled is not None:
        query = query.filter(Student.is_enrolled == is_enrolled)

    students = query.offset(skip).limit(limit).all()
    return students


# READ (one)
@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    responses={
        404: {"description": "Student not found"},
        422: {"description": "Invalid student ID"},
    },
    summary="Get a student by ID",
)
@limiter.limit("60/minute")
def get_student(request: Request, student_id: int, db: Session = Depends(get_db)):
    """Get a specific student by ID.

    - Looks up the student using the path parameter `student_id`.
    - Returns `404` when no matching student exists.
    """
    return get_student_or_404(db, student_id)


# READ (current user)
@router.get(
    "/me",
    response_model=StudentResponse,
    summary="Get the authenticated student's profile",
)
@limiter.limit("60/minute")
def get_my_profile(request: Request, current_user: Student = Depends(get_current_user)):
    """Return the authenticated user's profile.

    - Requires a valid bearer token.
    - Returns the student associated with the authenticated user.
    """
    return current_user


# UPDATE (full - PUT)
@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Replace a student's data",
)
@limiter.limit("20/minute")
def update_student(
    request: Request,
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
):
    """Fully replace a student's data.

    - Replaces all updateable fields for the selected student.
    - Requires a complete `StudentUpdate` request body.
    - Returns `404` when no matching student exists.
    """
    db_student = get_student_or_404(db, student_id)
    for field, value in student_data.model_dump().items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    return db_student


# UPDATE (partial - PATCH)
@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Student not found"},
        422: {"description": "Validation error"},
    },
    summary="Partially update a student",
)
@limiter.limit("20/minute")
def patch_student(
    request: Request,
    student_id: int,
    student_data: StudentPatch,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Partially update a student.

    - Requires an authenticated user.
    - Updates only the fields included in the request body.
    - Returns `404` when no matching student exists.
    """
    db_student = get_student_or_404(db, student_id)
    update_data = student_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    return db_student


# DELETE
@router.delete(
    "/{student_id}",
    status_code=204,
    summary="Delete a student",
)
@limiter.limit("20/minute")
def delete_student(
    request: Request,
    background_tasks: BackgroundTasks,
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a student.

    - Requires an authenticated user.
    - Removes the selected student from the database.
    - Records the deletion activity in the background.
    - Returns `404` when no matching student exists.
    """
    db_student = get_student_or_404(db, student_id)
    deleted_student_id = db_student.id

    db.delete(db_student)
    db.commit()

    background_tasks.add_task(
        log_activity,
        user_id=deleted_student_id,
        action="Student Deleted",
    )
