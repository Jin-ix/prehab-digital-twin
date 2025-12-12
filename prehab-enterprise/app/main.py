from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import auth, analytics
from app.db.base_class import Base
from app.db.session import engine

# === CRITICAL FIX: Import ALL models here ===
# This forces Python to "load" these files so SQLAlchemy knows they exist.
from app.models.user import User
from app.models.metrics import BiometricLog 
# ============================================

# 1. Create Tables on Startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 2. Register Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Digital Twin Engine"])

@app.get("/")
def root():
    return {"status": "Prehab System Secured & Ready"}