"""
Authentication API routes
API роути для авторизації
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import uuid

# Створюємо роутер
router = APIRouter()

# Налаштування безпеки
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Секретний ключ для JWT (в production має бути в env)
SECRET_KEY = "mova-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Mock база даних користувачів (в production має бути реальна БД)
users_db = {
    "admin@mova.com": {
        "id": "1",
        "email": "admin@mova.com",
        "username": "admin",
        "firstName": "Admin",
        "lastName": "User",
        "hashed_password": pwd_context.hash("password"),
        "role": {
            "id": "1",
            "name": "admin",
            "description": "Administrator",
            "permissions": [
                {"id": "1", "name": "dashboard:read", "description": "Read dashboard", "resource": "dashboard", "action": "read"},
                {"id": "2", "name": "files:manage", "description": "Manage files", "resource": "files", "action": "manage"},
                {"id": "3", "name": "ml:manage", "description": "Manage ML models", "resource": "ml", "action": "manage"},
            ]
        },
        "isActive": True,
        "emailVerified": True,
        "twoFactorEnabled": False,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
    }
}

# Pydantic моделі
class LoginRequest(BaseModel):
    email: str
    password: str
    rememberMe: Optional[bool] = False

class RegisterRequest(BaseModel):
    email: str
    username: str
    firstName: str
    lastName: str
    password: str
    confirmPassword: str
    acceptTerms: Optional[bool] = True

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    firstName: str
    lastName: str
    role: dict
    permissions: List[dict]
    isActive: bool
    emailVerified: bool
    twoFactorEnabled: bool
    createdAt: datetime
    updatedAt: datetime

class AuthResponse(BaseModel):
    user: UserResponse
    accessToken: str
    refreshToken: str
    expiresIn: int

class TokenRefreshRequest(BaseModel):
    refreshToken: str

class TokenRefreshResponse(BaseModel):
    accessToken: str
    refreshToken: str
    expiresIn: int

# Функції для роботи з токенами
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token():
    return str(uuid.uuid4())

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# Dependency для отримання поточного користувача
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = users_db.get(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# API endpoints
@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Вхід в систему"""
    print(f"Login attempt for email: {request.email}")
    print(f"Request data: {request}")
    
    user = users_db.get(request.email)
    if not user or not pwd_context.verify(request.password, user["hashed_password"]):
        print(f"Login failed for email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user["isActive"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    print(f"✅ User logged in successfully: {request.email}")
    
    # Створюємо токени
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    # Формуємо відповідь
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        firstName=user["firstName"],
        lastName=user["lastName"],
        role=user["role"],
        permissions=user["role"]["permissions"],
        isActive=user["isActive"],
        emailVerified=user["emailVerified"],
        twoFactorEnabled=user["twoFactorEnabled"],
        createdAt=user["createdAt"],
        updatedAt=user["updatedAt"],
    )
    
    return AuthResponse(
        user=user_response,
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresIn=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Реєстрація нового користувача"""
    print(f"Register attempt for email: {request.email}")
    print(f"Request data: {request}")
    
    if request.password != request.confirmPassword:
        print(f"Password mismatch for email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    if not request.acceptTerms:
        print(f"Terms not accepted for email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must accept the terms and conditions"
        )
    
    if request.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Створюємо нового користувача
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "email": request.email,
        "username": request.username,
        "firstName": request.firstName,
        "lastName": request.lastName,
        "hashed_password": pwd_context.hash(request.password),
        "role": {
            "id": "2",
            "name": "user",
            "description": "Regular User",
            "permissions": [
                {"id": "1", "name": "dashboard:read", "description": "Read dashboard", "resource": "dashboard", "action": "read"},
            ]
        },
        "isActive": True,
        "emailVerified": False,
        "twoFactorEnabled": False,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
    }
    
    users_db[request.email] = new_user
    
    print(f"✅ User registered successfully: {request.email}")
    
    # Створюємо токени
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user["email"]}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    # Формуємо відповідь
    user_response = UserResponse(
        id=new_user["id"],
        email=new_user["email"],
        username=new_user["username"],
        firstName=new_user["firstName"],
        lastName=new_user["lastName"],
        role=new_user["role"],
        permissions=new_user["role"]["permissions"],
        isActive=new_user["isActive"],
        emailVerified=new_user["emailVerified"],
        twoFactorEnabled=new_user["twoFactorEnabled"],
        createdAt=new_user["createdAt"],
        updatedAt=new_user["updatedAt"],
    )
    
    return AuthResponse(
        user=user_response,
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresIn=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(request: TokenRefreshRequest):
    """Оновлення токена"""
    # В реальному додатку тут має бути перевірка refresh token в базі
    # Для простоти просто створюємо новий токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": "admin@mova.com"}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    return TokenRefreshResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresIn=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout():
    """Вихід з системи"""
    return {"message": "Successfully logged out"}

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Отримання профілю користувача"""
    user_response = UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        firstName=current_user["firstName"],
        lastName=current_user["lastName"],
        role=current_user["role"],
        permissions=current_user["role"]["permissions"],
        isActive=current_user["isActive"],
        emailVerified=current_user["emailVerified"],
        twoFactorEnabled=current_user["twoFactorEnabled"],
        createdAt=current_user["createdAt"],
        updatedAt=current_user["updatedAt"],
    )
    return user_response 