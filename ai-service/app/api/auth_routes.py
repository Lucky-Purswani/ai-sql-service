import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.db.models import User, EmailVerification, RefreshToken, LoginAudit
from app.models.auth_models import (
    UserSignupRequest, UserSignupResponse,
    UserLoginRequest, TokenResponse,
    VerifyEmailRequest
)
from app.services.auth_service import (
    get_password_hash, verify_password,
    create_access_token, generate_refresh_token, generate_otp
)
from app.services.email_service import send_verification_email

router = APIRouter()

def hash_token(token: str) -> str:
    """Hashes a token or OTP using SHA-256 for fast, secure database lookups."""
    return hashlib.sha256(token.encode()).hexdigest()

# ==========================================
# 1. Signup
# ==========================================
@router.post("/signup", response_model=UserSignupResponse)
def signup(request: UserSignupRequest, db: Session = Depends(get_db)):
    # 1. Validate password match
    if request.password != request.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # 2. Check if email already exists
    email_lower = request.email.lower()
    existing_user = db.query(User).filter(User.email == email_lower).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 3. Create User
    try:
        new_user = User(
            email=email_lower,
            password_hash=get_password_hash(request.password),
            is_verified=False
        )
        db.add(new_user)
        db.flush() # Get the new_user.id without committing yet
        
        # 4. Generate OTP
        otp_plain = generate_otp()
        otp_hashed = hash_token(otp_plain)
        
        verification = EmailVerification(
            user_id=new_user.id,
            otp_hash=otp_hashed,
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10)
        )
        db.add(verification)
        
        # 5. Commit Transaction
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating your account. Please try again later.")
    
    # 6. Send Real Email
    send_verification_email(to_email=email_lower, otp=otp_plain)
    
    return UserSignupResponse(
        message="User created. Please check your email for the OTP.",
        user_id=new_user.id # type: ignore
    )

# ==========================================
# 2. Verify Email
# ==========================================
@router.post("/verify-email")
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    email_lower = request.email.lower()
    user = db.query(User).filter(User.email == email_lower).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.is_verified:
        return {"message": "Email is already verified"}
        
    otp_hashed = hash_token(request.otp)
    
    # Find the verification record
    verification = db.query(EmailVerification).filter(
        EmailVerification.user_id == user.id,
        EmailVerification.otp_hash == otp_hashed,
        EmailVerification.is_used == False
    ).first()
    
    if not verification:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    if datetime.now(timezone.utc).replace(tzinfo=None) > verification.expires_at: # type: ignore
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    # Mark as verified
    try:
        verification.is_used = True # type: ignore
        user.is_verified = True # type: ignore
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Verification failed. Please try again.")
    
    return {"message": "Email successfully verified. You can now login."}

# ==========================================
# 3. Login
# ==========================================
@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, response: Response, client_request: Request, db: Session = Depends(get_db)):
    email_lower = request.email.lower()
    user = db.query(User).filter(User.email == email_lower).first()
    
    # Log the attempt
    client_ip = client_request.client.host if client_request.client else "unknown"
    
    if not user:
        _log_audit(db, None, email_lower, client_ip, False)
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    # Check Lockout
    if user.locked_until and datetime.now(timezone.utc).replace(tzinfo=None) < user.locked_until: # type: ignore
        raise HTTPException(status_code=403, detail="Account is temporarily locked due to too many failed attempts.")
        
    # Verify Password
    if not verify_password(request.password, user.password_hash): # type: ignore
        user.failed_login_attempts += 1 # type: ignore
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=15) # type: ignore
        db.commit()
        _log_audit(db, user.id, email_lower, client_ip, False)
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in.")
        
    # Success! Reset locks
    user.failed_login_attempts = 0 # type: ignore
    user.locked_until = None # type: ignore
    _log_audit(db, user.id, email_lower, client_ip, True)
    
    # Generate Tokens
    access_token = create_access_token(str(user.id), str(user.email)) # type: ignore
    refresh_token_plain = generate_refresh_token()
    
    # Save Refresh Token
    family_id = uuid.uuid4()
    try:
        db_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token_plain),
            family_id=family_id,
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7)
        )
        db.add(db_token)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Login failed while saving session.")
    
    # Set Secure Cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_plain,
        httponly=True,
        secure=False, # Set to True in production (requires HTTPS)
        samesite="lax",
        max_age=7 * 24 * 60 * 60 # 7 days
    )
    
    return TokenResponse(access_token=access_token)

# ==========================================
# 4. Refresh Token (Token Rotation)
# ==========================================
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    token_plain = request.cookies.get("refresh_token")
    if not token_plain:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    token_hashed = hash_token(token_plain)
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hashed).first()
    
    if not db_token:
        response.delete_cookie("refresh_token")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    # Reuse Detection Security
    if db_token.is_revoked:
        # A revoked token was used! This implies token theft.
        # Immediately revoke ALL tokens in this family.
        db.query(RefreshToken).filter(RefreshToken.family_id == db_token.family_id).update({"is_revoked": True})
        db.commit()
        response.delete_cookie("refresh_token")
        raise HTTPException(status_code=401, detail="Security alert: Token reuse detected. All sessions revoked.")
        
    if datetime.now(timezone.utc).replace(tzinfo=None) > db_token.expires_at: # type: ignore
        raise HTTPException(status_code=401, detail="Refresh token expired")
        
    # Token is valid. Rotate it.
    db_token.is_revoked = True # type: ignore
    
    user = db_token.user
    new_access_token = create_access_token(user.id, user.email)
    new_refresh_plain = generate_refresh_token()
    
    try:
        new_db_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh_plain),
            family_id=db_token.family_id, # Keep same family
            expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7)
        )
        db.add(new_db_token)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Token refresh failed.")
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_plain,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    
    return TokenResponse(access_token=new_access_token)


# ==========================================
# Helper
# ==========================================
def _log_audit(db: Session, user_id, email: str, ip: str, success: bool):
    audit = LoginAudit(user_id=user_id, email=email, ip_address=ip, success=success)
    db.add(audit)
    db.commit()
