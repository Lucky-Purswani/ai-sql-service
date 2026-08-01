from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.config import settings

# HTTPBearer extracts the JWT token from the "Authorization: Bearer <token>" header.
# This is the standard way React (or any frontend) sends auth tokens.
bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    JWT Middleware — equivalent to a Node.js `authenticateToken` middleware.

    This function is injected into any route that needs a logged-in user.
    It:
      1. Reads the 'Authorization: Bearer <token>' header
      2. Decodes and validates the JWT signature using our SECRET_KEY
      3. If valid → returns the token payload (which contains the user's id and email)
      4. If expired or tampered → throws a 401 Unauthorized error

    Usage in routes:
      @router.get("/protected")
      def my_route(user: dict = Depends(get_current_user)):
          return {"user_id": user["sub"]}
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        # "sub" (subject) is the standard JWT field we will store the user's ID in.
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token payload is missing user ID.")
        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or has expired.")
