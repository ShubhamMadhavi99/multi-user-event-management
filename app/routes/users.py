from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate  # Added missing import
from app.services.auth import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
import os

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Master Admin Credentials (Load from .env)
MASTER_ADMIN_USERNAME = os.getenv("MASTER_ADMIN_USERNAME", "masteradmin")
MASTER_ADMIN_PASSWORD = os.getenv("MASTER_ADMIN_PASSWORD", "masteradmin")


# ------------------------
# 🔹 Helper Function for Admin Check
# ------------------------
def is_admin(user: User):
    """Check if the given user is an admin. Raises an exception if not."""
    if not user or not user.role or user.role.lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Admins only.")


# ------------------------
# 🔹 Register New User (Admins Only)
# ------------------------
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows only Admins to create new users. Prevents creating 'masteradmin'."""
    payload = decode_access_token(token)
    requester_role = payload.get("role", "").lower()

    # Ensure only admins can register new users
    if requester_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create new users.")

    # Prevent users from registering as 'masteradmin'
    if user.username.lower() == MASTER_ADMIN_USERNAME.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This username is reserved for the system.")

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    # Hash password and create new user
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, password=hashed_password, role=user.role)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")


# ------------------------
# 🔹 User Login & Token Generation
# ------------------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and generate JWT token."""
    
    # Master Admin Login (Bypass DB Query)
    if form_data.username == MASTER_ADMIN_USERNAME and form_data.password == MASTER_ADMIN_PASSWORD:
        access_token = create_access_token({"sub": MASTER_ADMIN_USERNAME, "role": "admin"}, timedelta(hours=3))
        return {"access_token": access_token, "token_type": "bearer"}

    # Query user from DB
    user = db.query(User).filter(User.username == form_data.username).first()

    # Normal User Authentication
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.username, "role": user.role}, timedelta(hours=3))
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------
# 🔹 List All Users (Admins & Master Admin Only)
# ------------------------
@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows only Admins and Master Admin to list all users."""
    payload = decode_access_token(token)
    requester_role = payload.get("role", "").lower()
    requester_username = payload.get("sub")

    # Check if requester is an Admin or Master Admin
    if requester_role != "admin" and requester_username != MASTER_ADMIN_USERNAME:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Admins only.")

    return db.query(User).all()


# ------------------------
# 🔹 Get User by ID (Admins & Master Admin Only)
# ------------------------
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows Admins and Master Admin to fetch a user by ID."""
    payload = decode_access_token(token)
    requester_username = payload.get("sub")
    requester_role = payload.get("role", "").lower()

    # Ensure only Admins or Master Admin can access this API
    if requester_role != "admin" and requester_username != MASTER_ADMIN_USERNAME:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Admins only.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


# ------------------------
# 🔹 Update User (Admins & Master Admin Only)
# ------------------------
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows only Admins and Master Admin to update user details."""
    payload = decode_access_token(token)
    requester_username = payload.get("sub")
    requester_role = payload.get("role", "").lower()

    # Ensure only Admins or Master Admin can access this API
    if requester_role != "admin" and requester_username != MASTER_ADMIN_USERNAME:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Admins only.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_update.username:
        user.username = user_update.username
    if user_update.password:
        user.password = hash_password(user_update.password)
    if user_update.role:
        user.role = user_update.role

    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Update failed: {str(e)}")


# ------------------------
# 🔹 Delete User (Admins & Master Admin Only)
# ------------------------
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Allows only Admins and Master Admin to delete a user."""
    payload = decode_access_token(token)
    requester_username = payload.get("sub")
    requester_role = payload.get("role", "").lower()

    # Ensure only Admins or Master Admin can access this API
    if requester_role != "admin" and requester_username != MASTER_ADMIN_USERNAME:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Admins only.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Deletion failed: {str(e)}")
