import secrets
from datetime import datetime, timedelta, timezone
from jose import jwt
import bcrypt
from app.core.config import settings

# ==========================================
# Password Hashing Setup
# ==========================================
# We use bcrypt directly to avoid passlib incompatibilities with bcrypt >= 4.0

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if a plain text password matches the stored hash."""
    # bcrypt requires bytes, so we encode strings to utf-8
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hashes a plain text password for safe storage."""
    # Passwords longer than 72 bytes are not supported by standard bcrypt.
    # We truncate it to 72 bytes to prevent bcrypt 4.0+ from throwing a ValueError.
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


# ==========================================
# JWT Access Tokens
# ==========================================
def create_access_token(user_id: str, email: str) -> str:
    """
    Creates a short-lived JSON Web Token (JWT) used for accessing protected routes.
    The payload contains the user_id (as 'sub') and their email.
    """
    expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES) # type: ignore
    
    to_encode = {
        "sub": str(user_id), # type: ignore
        "email": email,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


# ==========================================
# Refresh Tokens
# ==========================================
def generate_refresh_token() -> str:
    """
    Generates a cryptographically strong random string to be used as a Refresh Token.
    This token is NOT a JWT. It's an opaque string (like a password) that will be 
    sent to the user via a secure httpOnly cookie.
    We will hash this string before storing it in the database.
    """
    return secrets.token_urlsafe(64)


# ==========================================
# OTP Generation (Email Verification)
# ==========================================
def generate_otp() -> str:
    """
    Generates a random 6-digit number (as a string) for email verification.
    Like passwords and refresh tokens, we will hash this before storing it in the DB.
    """
    # Generate a random number between 100000 and 999999
    # Using secrets.randbelow is cryptographically secure.
    otp_int = 100000 + secrets.randbelow(900000)
    return str(otp_int)
