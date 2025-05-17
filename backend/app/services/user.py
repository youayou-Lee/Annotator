from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate, ApprovalRequest

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def get_pending_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.status == UserStatus.pending).offset(skip).limit(limit).all()

def get_superuser(db: Session) -> Optional[User]:
    return db.query(User).filter(User.role == UserRole.superuser).first()

def create_user(db: Session, user: UserCreate) -> User:
    from app.core.security import get_password_hash
    hashed_password = get_password_hash(user.password)
    
    # 默认状态设置
    status = UserStatus.pending
    # 如果是标注人员，自动批准
    if user.role == UserRole.annotator:
        status = UserStatus.approved
    # 如果是超级管理员且系统中没有超级管理员，自动批准
    elif user.role == UserRole.superuser and not get_superuser(db):
        status = UserStatus.approved
        
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        role=user.role,
        status=status
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    from app.core.security import get_password_hash
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def approve_user(db: Session, approval_request: ApprovalRequest, approved_by_id: int) -> Optional[User]:
    db_user = get_user(db, approval_request.user_id)
    if not db_user:
        return None
    
    db_user.status = approval_request.status
    db_user.approval_date = datetime.utcnow()
    db_user.approved_by_id = approved_by_id
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    from app.core.security import verify_password
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    # 只有已批准的用户可以登录
    if user.status != UserStatus.approved:
        return None
    return user 

def get_users_by_role(db: Session, role: UserRole, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()

def get_pending_admins(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).filter(
        User.role == UserRole.admin,
        User.status == UserStatus.pending
    ).offset(skip).limit(limit).all() 