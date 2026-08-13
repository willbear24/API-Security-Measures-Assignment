from fastapi import FastAPI
from app.config import settings
from app.routers import students
from app.database import engine, Base

app = FastAPI(
    title=settings.app_name,
    description="Student CRUD Demo API",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine) # Creates the table if it not exist

app.include_router(students.router)
