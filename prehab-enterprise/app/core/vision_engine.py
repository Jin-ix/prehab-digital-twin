import cv2
import math
import numpy as np
from ultralytics import YOLO

class VisionEngine:
    def __init__(self):
        # Load YOLOv8 Pose Model
        self.model = YOLO('yolov8n-pose.pt') 

    def calculate_angle(self, p1, p2, p3):
        """Calculates angle between 3 points (p1-p2-p3)"""
        v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
        v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
        
        dot_prod = np.dot(v1, v2)
        mag1 = np.linalg.norm(v1)
        mag2 = np.linalg.norm(v2)
        
        if mag1 == 0 or mag2 == 0: return 180.0
        
        cos_angle = dot_prod / (mag1 * mag2)
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    def analyze_video(self, video_path: str):
        cap = cv2.VideoCapture(video_path)
        
        valgus_angles = []
        shin_angles = []
        hip_deviations = [] # Normalized deviation
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            frame_count += 1
            if frame_count % 3 != 0: # Process every 3rd frame (more samples = better accuracy)
                continue
            
            results = self.model(frame, verbose=False)
            
            for result in results:
                if result.keypoints and result.keypoints.data is not None:
                    kpts = result.keypoints.data[0].cpu().numpy()
                    if len(kpts) < 17: continue

                    # === COORDINATES (Right Leg) ===
                    # Hip(12), Knee(14), Ankle(16)
                    r_hip = kpts[12][:2]
                    r_knee = kpts[14][:2]
                    r_ankle = kpts[16][:2]
                    
                    # Skip empty detections
                    if np.any(r_hip == 0) or np.any(r_knee == 0) or np.any(r_ankle == 0):
                        continue

                    # 1. LEG LENGTH (For Normalization)
                    # Distance from Hip to Ankle
                    leg_length = np.linalg.norm(r_hip - r_ankle)
                    if leg_length == 0: continue

                    # 2. HIP INTERNAL ROTATION (Normalized)
                    # Logic: Draw a line from Hip to Ankle. How far is the Knee from this line?
                    # Start with Midpoint X
                    midpoint_x = (r_hip[0] + r_ankle[0]) / 2
                    
                    # Deviation: Knee X position relative to the center line
                    raw_deviation = r_knee[0] - midpoint_x 
                    
                    # Normalize: Deviation as a % of leg length
                    # e.g., 0.05 means knee moved 5% of leg length inward
                    normalized_deviation = raw_deviation / leg_length
                    hip_deviations.append(normalized_deviation)

                    # 3. KNEE VALGUS (Angle)
                    angle = self.calculate_angle(r_hip, r_knee, r_ankle)
                    valgus_angles.append(abs(180 - angle))

                    # 4. FOOT STRIKE (Shin Angle)
                    dx = r_knee[0] - r_ankle[0]
                    dy = r_knee[1] - r_ankle[1]
                    if dy != 0:
                        shin_angles.append(math.degrees(math.atan2(dx, dy)))

        cap.release()

        # === INTELLIGENT SCORING ===
        
        # A. Valgus (Angle)
        avg_valgus = float(np.percentile(valgus_angles, 85)) if valgus_angles else 0.0

        # B. Hip Rotation (Normalized Ratio)
        # Threshold: If knee deviates > 4% of leg length (0.04), it's an issue.
        # Note: We use absolute value to catch both inward and outward, 
        # but internal rotation is usually the concern.
        avg_hip_ratio = float(np.mean(np.abs(hip_deviations))) if hip_deviations else 0.0
        
        hip_status = "Normal"
        if avg_hip_ratio > 0.04:  # SENSITIVITY SETTING (Lower = More Sensitive)
            hip_status = "Excessive Internal Rotation"

        # C. Foot Strike
        avg_shin = float(np.mean(shin_angles)) if shin_angles else 0.0
        strike_type = "Midfoot/Forefoot" if avg_shin > -5 else "Heel Strike (Overstride)"

        # DEBUGGING: Print hidden stats to terminal so you can see what happened
        print(f"DEBUG STATS -> Valgus: {avg_valgus:.1f}, Hip Ratio: {avg_hip_ratio:.4f}, Shin: {avg_shin:.1f}")

        return {
            "valgus": avg_valgus,
            "hip_rotation": hip_status,
            "foot_strike": strike_type
        }