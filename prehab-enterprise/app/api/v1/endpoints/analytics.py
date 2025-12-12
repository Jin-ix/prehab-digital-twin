import shutil
import os
from fastapi import APIRouter, Depends, File, UploadFile
from app.api import deps
from app.models.user import User
from app.services.analysis_service import AnalysisService
from app.core.vision_engine import VisionEngine

# Import all sub-models used in the code
from app.schemas.analytics import (
    AnalysisInput, 
    AnalysisResponse, 
    MechanicsInput, 
    LoadInput
)

router = APIRouter()

# Initialize Services
analyzer = AnalysisService()
vision_model = VisionEngine()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_my_data(
    data: AnalysisInput, 
    current_user: User = Depends(deps.get_current_user)
):
    """
    Standard Endpoint: Accepts JSON data (manual entry) and returns risk report.
    """
    return await analyzer.process_metrics(current_user, data)

@router.post("/analyze/video", response_model=AnalysisResponse)
async def analyze_video_upload(
    file: UploadFile = File(...), 
    current_user: User = Depends(deps.get_current_user)
):
    """
    AI Vision Endpoint:
    1. Receives a video file.
    2. Runs YOLOv8 Pose Estimation (Valgus, Hip, Foot Strike).
    3. Feeds that data into the Digital Twin.
    4. Returns the Injury Risk Report.
    """
    # 1. Save the video temporarily
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Run AI Vision (Get Dictionary of results)
        vision_results = vision_model.analyze_video(temp_filename)
        
        # 3. Feed data into Digital Twin Logic
        # Extract new metrics
        detected_valgus = vision_results["valgus"]
        detected_hip = vision_results["hip_rotation"]
        detected_strike = vision_results["foot_strike"]

        ai_data = AnalysisInput(
            mechanics=MechanicsInput(
                knee_valgus_angle=detected_valgus,
                hip_internal_rotation=detected_hip,    # <--- NEW
                foot_strike_pattern=detected_strike,   # <--- NEW
                head_forward_angle=0.0 
            ),
            load_metrics=LoadInput(acwr=1.0) # Default load
        )
        
        # 4. Get the Prescription/Report from the Brain
        report = await analyzer.process_metrics(current_user, ai_data)
        return report

    finally:
        # Cleanup: Delete the video file to save space
        if os.path.exists(temp_filename):
            os.remove(temp_filename)