# Create Pydantic schemas: StudentCreate, StudentUpdate (full), StudentPatch (partial), StudentResponse

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class StudentCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="The student's full name",
        examples=["Jane Doe"],
    )
    email: str = Field(
        min_length=1,
        max_length=200,
        description="The student's school email address",
        examples=["jane@example.edu"],
    )
    grade_level: int = Field(
        ge=1,
        le=12,
        description="The student's current grade level, from 1 through 12",
        examples=[10],
    )
    gpa: Optional[float] = Field(
        default=None,
        gt=0,
        description="The student's grade point average",
        examples=[3.8],
    )
    is_enrolled: bool = Field(
        default=True,
        description="Whether the student is currently enrolled",
        examples=[True],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jane@example.edu",
                "grade_level": 10,
                "gpa": 3.8,
                "is_enrolled": True,
            }
        }
    )

class StudentUpdate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="The student's full name",
        examples=["Jane Doe"],
    )
    email: str = Field(
        min_length=1,
        max_length=200,
        description="The student's school email address",
        examples=["jane@example.edu"],
    )
    grade_level: int = Field(
        ge=1,
        le=12,
        description="The student's current grade level, from 1 through 12",
        examples=[10],
    )
    gpa: Optional[float] = Field(
        default=None,
        gt=0,
        description="The student's grade point average",
        examples=[3.8],
    )
    is_enrolled: bool = Field(
        default=True,
        description="Whether the student is currently enrolled",
        examples=[True],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jane@example.edu",
                "grade_level": 10,
                "gpa": 3.8,
                "is_enrolled": True,
            }
        }
    )

class StudentPatch(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="The student's full name",
        examples=["Jane Doe"],
    )
    email: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="The student's school email address",
        examples=["jane@example.edu"],
    )
    grade_level: Optional[int] = Field(
        default=None,
        ge=1,
        le=12,
        description="The student's current grade level, from 1 through 12",
        examples=[10],
    )
    gpa: Optional[float] = Field(
        default=None,
        gt=0,
        description="The student's grade point average",
        examples=[3.8],
    )
    is_enrolled: Optional[bool] = Field(
        default=None,
        description="Whether the student is currently enrolled",
        examples=[True],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "gpa": 3.9,
            }
        }
    )

class StudentResponse(BaseModel):
    id: int = Field(description="The unique identifier for the student")
    name: str = Field(description="The student's full name")
    email: str = Field(description="The student's school email address")
    grade_level: int = Field(
        description="The student's current grade level, from 1 through 12"
    )
    gpa: Optional[float] = Field(description="The student's grade point average")
    is_enrolled: bool = Field(
        description="Whether the student is currently enrolled"
    )
    created_at: datetime = Field(description="When the student record was created")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Jeff Buckley",
                "email": "jeff@fake.edu",
                "grade_level": 12,
                "gpa": 4.0,
                "is_enrolled": True,
                "created_at": "2026-02-24T10:30:00",
            }
        },
    )


