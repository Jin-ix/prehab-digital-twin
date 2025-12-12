from sqlalchemy import Column, Integer, Float, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class BiometricLog(Base):
    __tablename__ = "biometric_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Shared Metrics
    steps = Column(Integer, default=0)
    sleep_hours = Column(Float, nullable=True)
    
    # B2B Specific
    vo2_max = Column(Float, nullable=True)
    acwr_ratio = Column(Float, nullable=True)
    
    # AI Results
    ai_insights = Column(JSON, nullable=True)

    user = relationship("User", back_populates="biometrics")