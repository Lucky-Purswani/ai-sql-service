from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

# ==========================================
# Signup
# ==========================================
class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    password_confirm: str

class UserSignupResponse(BaseModel):
    message: str
    user_id: UUID

# ==========================================
# Login
# ==========================================
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ==========================================
# OTP Verification
# ==========================================
class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

# ==========================================
# Session / Profile
# ==========================================
class UserProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_verified: bool

# ==========================================
# Database Connection
# ==========================================
class AddConnectionRequest(BaseModel):
    nickname: str = Field(..., description="A friendly name for your database, e.g. 'Production Postgres'")
    db_url: str = Field(..., description="The full postgresql:// connection string")

class AddConnectionResponse(BaseModel):
    message: str
    connection_id: UUID
    tables_synced: int

class ConnectionResponse(BaseModel):
    id: UUID
    nickname: str
    created_at: str # ISO format string for frontend parsing

class ConnectionListResponse(BaseModel):
    connections: list[ConnectionResponse]

# ==========================================
# Query Execution
# ==========================================
class QueryRequest(BaseModel):
    connection_id: UUID
    question: str

class QueryResponse(BaseModel):
    summary: str
    sql_used: str
    columns: list[str]
    sample_rows: list[dict]
    total_rows: int

class ExportRequest(BaseModel):
    connection_id: UUID
    sql_used: str   # The already-validated SQL from a previous query result
    filename: str = "export"  # Optional custom filename
