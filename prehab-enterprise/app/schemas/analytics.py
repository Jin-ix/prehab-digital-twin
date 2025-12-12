from pydantic import BaseModel
from typing import Optional, List

# === UPDATED INPUTS ===
class MechanicsInput(BaseModel):
    knee_valgus_angle: Optional[float] = 0.0
    hip_internal_rotation: Optional[str] = "Normal" # New Field
    foot_strike_pattern: Optional[str] = "Unknown"  # New Field
    head_forward_angle: Optional[float] = 0.0

class LoadInput(BaseModel):
    acwr: Optional[float] = 0.0
    sprint_distance: Optional[float] = 0.0

class DailyInput(BaseModel):
    steps: int
    pain_areas: List[str] = []

class AnalysisInput(BaseModel):
    mechanics: Optional[MechanicsInput] = None
    load_metrics: Optional[LoadInput] = None
    daily_stats: Optional[DailyInput] = None

# === OUTPUTS ===
class AnalysisResponse(BaseModel):
    user_id: int
    report_type: str
    score: int
    alerts: List[str]
    recommendations: List[str]