from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COACH = "coach"
    ATHLETE = "athlete"
    PUBLIC = "public"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="public")
    
    # B2B: Organization Link
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    organization = relationship("Organization", back_populates="users")
    biometrics = relationship("BiometricLog", back_populates="user")
    
class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    subscription_tier = Column(String)
    users = relationship("User", back_populates="organization")