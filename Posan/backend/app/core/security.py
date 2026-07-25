from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError
import bcrypt
from app.core.config import settings
from app.core.database import get_db


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Dictionary containing claims to encode
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


import logging
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError

# Initialize Keycloak OpenID client
keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_SERVER_URL,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    realm_name=settings.KEYCLOAK_REALM_NAME,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
)

def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify a Keycloak JWT token.
    """
    try:
        # Get public key from Keycloak if you want local verification,
        # but here we use Keycloak's introspection or decode locally if JWKS is fetched.
        # The simplest way for now is just decode without verification if API Gateway handles it,
        # but for security, we fetch the certs and verify:
        KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
        options = {"verify_signature": True, "verify_aud": False, "exp": True}
        payload = keycloak_openid.decode_token(
            token,
            key=KEYCLOAK_PUBLIC_KEY,
            options=options
        )
        return payload
    except KeycloakError as e:
        logging.error(f"Keycloak error validating token: {e}")
        return None
    except Exception as e:
        logging.error(f"Error validating token: {e}")
        return None

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# Create HTTP Bearer security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current user from Keycloak JWT token with JIT provisioning.
    """
    from app.models.user import User, UserRole
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Keycloak uses 'sub' as the unique identifier
    keycloak_id = payload.get("sub")
    email = payload.get("email")
    username = payload.get("preferred_username") or payload.get("name") or email
    
    if keycloak_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Try to find user by keycloak_id first
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    
    # Fallback to email if keycloak_id is not set yet (migration scenario)
    if user is None and email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.keycloak_id = keycloak_id
            db.commit()
            db.refresh(user)
    
    # JIT (Just-In-Time) Provisioning
    if user is None:
        if not email:
            email = f"{username}@posan.local" # Fallback if email is not provided in token
        
        user = User(
            email=email,
            username=username,
            keycloak_id=keycloak_id,
            hashed_password=None, # Managed by Keycloak
            full_name=payload.get("name"),
            role=UserRole.CHILD # Default role, can be mapped from Keycloak roles
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

