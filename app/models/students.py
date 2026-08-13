# Create a Student SQLAlchemy model:
# id (integer, primary key)
# name (string, required)
# email (string, unique, required)
# grade_level (integer, 1-12)
# gpa (float, optional)
# is_enrolled (boolean, default True)
# created_at (datetime, auto-generated)

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    grade_level = Column(Integer)
    gpa = Column(Float, nullable=True)
    is_enrolled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


