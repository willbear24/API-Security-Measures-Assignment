# Create Pydantic schemas: StudentCreate, StudentUpdate (full), StudentPatch (partial), StudentResponse

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=200)
    grade_level: int = Field(gt=0, lt=13)
    gpa: Optional[float] = Field(default=None, gt=0)
    is_enrolled: bool = Field(default=True)

class StudentUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=200)
    grade_level: int = Field(ge=1, le=12)
    gpa: Optional[float] = Field(default=None, gt=0)
    is_enrolled: bool = Field(default=True)

class StudentPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, min_length=1, max_length=200)
    grade_level: Optional[int] = Field(default=None, gt=0, lt=13)
    gpa: Optional[float] = Field(default=None, gt=0)
    is_enrolled: Optional[bool] = Field(default=None)

class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    grade_level: int
    gpa: Optional[float]
    is_enrolled: bool
    created_at: datetime

    class Config:
        from_attributes = True


