from fastapi import FastAPI
from app.config import settings
from app.routers import auth, students
from app.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter

# Security measures currently implemented:
# - CORS allows only the configured local frontend origins (localhost:8501 and
#   localhost:3000), allows credentials, and restricts methods to the API's
#   GET/POST/PUT/PATCH/DELETE methods.
# - SlowAPI rate limiting uses the client's remote address: registration is
#   limited to 20 requests per minute and login to 5 requests per minute.
# - HTTP Bearer authentication protects the current-profile, create, patch,
#   and delete student endpoints.
# - JWTs use HS256, include a 30-minute expiration, and are rejected when they
#   are invalid, expired, missing a subject, or reference no existing user.
# - Passwords are hashed with bcrypt through Passlib and are verified against
#   the stored hash during login; plaintext passwords are not stored.
# - Pydantic validates request bodies, including required fields, string
#   lengths, minimum password length (8), grade levels (1-12), and positive
#   GPAs.
# - SQLAlchemy queries use bound parameters, and student email addresses have
#   a database-level unique constraint to prevent duplicate accounts.
# - Database writes use commits and rollbacks for duplicate-email conflicts;
#   errors return controlled 401, 404, and 409 responses instead of raw errors.
# - Response schemas expose selected student fields and do not expose the
#   stored hashed_password column.
#
# Security caveats for this development project:
# - SECRET_KEY is hard-coded for development and must come from a strong,
#   private environment variable in production.
# - settings.debug defaults to True and should be disabled in production.
# - GET /students/, GET /students/{student_id}, and PUT /students/{student_id}
#   currently do not require authentication; add the auth dependency if they
#   should be protected.
# - CORS origins, JWT configuration, and rate-limit storage are local/demo
#   settings; review them before deploying behind a proxy or multiple workers.
tags_metadata = [
    {"name": "Authentication", "description": "User registration and login. All protected endpoints require a Bearer token."},
    {"name": "Students", "description": "CRUD operations for students. Some endpoints require authentication."},
]

app = FastAPI(
    title="""Student CRUD Demo API""",
    description="""A full-featured student management API with JWT authentication, Pydantic validation and SQLAlchemy persistence.
    
    ## Quick Start
    1. Register at `POST /auth/register`
    2. Copy the `access_token` from the response,
    3. Click **Authorize** above and paste the token,
    4. Start creating and managing students! """,

    version="1.0.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"]
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Base.metadata.create_all(bind=engine) # Creates the table if it not exist

app.include_router(students.router)
app.include_router(auth.router)
