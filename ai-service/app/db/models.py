import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer,
    DateTime, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.connection import Base


# ==========================================
# User Table
# ==========================================
class User(Base):
    __tablename__ = "users"

    id                    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email                 = Column(String(255), unique=True, nullable=False, index=True)
    password_hash         = Column(String(255), nullable=False)           # bcrypt hash, never plain text
    is_verified           = Column(Boolean, default=False, nullable=False) # Email must be verified before login works
    failed_login_attempts = Column(Integer, default=0, nullable=False)    # Counts wrong passwords
    locked_until          = Column(DateTime, nullable=True)               # Account locked until this time (brute force protection)
    created_at            = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships (like Prisma's `include`)
    refresh_tokens        = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    email_verifications   = relationship("EmailVerification", back_populates="user", cascade="all, delete-orphan")
    connections           = relationship("DatabaseConnection", back_populates="user", cascade="all, delete-orphan")
    audit_logs            = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    login_audits          = relationship("LoginAudit", back_populates="user", cascade="all, delete-orphan")


# ==========================================
# Email Verification Table
# ==========================================
class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    otp_hash       = Column(String(255), nullable=False)   # Hashed OTP (we never store OTPs in plain text)
    expires_at     = Column(DateTime, nullable=False)      # OTP valid for 10 minutes
    is_used        = Column(Boolean, default=False)        # One-time use only
    resend_count   = Column(Integer, default=0)            # Max 3 resends per hour
    last_resent_at = Column(DateTime, nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="email_verifications")


# ==========================================
# Refresh Token Table
# ==========================================
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash  = Column(String(255), nullable=False, index=True) # SHA-256 hash of the actual token (never store raw)
    family_id   = Column(UUID(as_uuid=True), nullable=False)      # All tokens in same login share a family_id.
                                                                   # If a revoked token is reused, the ENTIRE family is revoked.
    expires_at  = Column(DateTime, nullable=False)
    is_revoked  = Column(Boolean, default=False, nullable=False)
    device_info = Column(String(255), nullable=True)   # User-Agent string (optional, for session listing)
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")


# ==========================================
# Database Connection Table
# ==========================================
class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id          = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    nickname         = Column(String(100), nullable=False)      # e.g., "Company Postgres"
    encrypted_db_url = Column(Text, nullable=False)             # Fernet-encrypted full connection string
    created_at       = Column(DateTime, default=datetime.utcnow)

    user       = relationship("User", back_populates="connections")
    audit_logs = relationship("AuditLog", back_populates="connection", cascade="all, delete-orphan")


# ==========================================
# Query Audit Log Table
# ==========================================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id       = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("database_connections.id", ondelete="CASCADE"), nullable=True)
    question      = Column(Text, nullable=False)
    sql_generated = Column(Text, nullable=True)
    status        = Column(String(20), nullable=False)  # "SUCCESS" or "ERROR"
    row_count     = Column(Integer, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    user       = relationship("User", back_populates="audit_logs")
    connection = relationship("DatabaseConnection", back_populates="audit_logs")


# ==========================================
# Login Audit Table (security monitoring)
# ==========================================
class LoginAudit(Base):
    __tablename__ = "login_audits"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # nullable: email might not exist
    email      = Column(String(255), nullable=False)  # Always log the email that was attempted
    ip_address = Column(String(45), nullable=True)    # IPv4 or IPv6
    success    = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="login_audits")
