from app.models.user import User
from app.schemas.analytics import AnalysisInput

class AnalysisService:
    
    async def process_metrics(self, user: User, data: AnalysisInput):
        """
        Master function: Routes to the correct analysis engine based on Role.
        """
        if user.role == "athlete" or user.role == "coach":
            return self._analyze_pro_athlete(user, data)
        else:
            return self._analyze_common_user(user, data)

    def _analyze_pro_athlete(self, user, data):
        # === B2B LOGIC: High Performance & Injury Risk ===
        risk_score = 0
        alerts = []
        rehab_plan = []

        # 1. Check Workload (ACWR)
        if data.load_metrics and data.load_metrics.acwr > 1.3:
            risk_score += 40
            alerts.append("CRITICAL: ACWR > 1.3 (High Injury Risk)")
            rehab_plan.append("Reduce training load by 40% immediately.")

        # 2. Check Mechanics (Knee Valgus)
        if data.mechanics and data.mechanics.knee_valgus_angle > 15:
            risk_score += 30
            alerts.append("Biomechanics: Hazardous Knee Valgus detected")
            rehab_plan.append("Rx: Banded Clamshells & Glute Bridges")

        # 3. Check Hip Rotation (NEW)
        if data.mechanics and data.mechanics.hip_internal_rotation == "Excessive Internal Rotation":
            risk_score += 25
            alerts.append("Hip Mechanics: Lack of external rotator control")
            rehab_plan.append("Rx: Monster Walks (Band around knees)")

        # 4. Check Foot Strike (NEW)
        if data.mechanics and data.mechanics.foot_strike_pattern == "Heel Strike (Overstride)":
            risk_score += 15
            alerts.append("Running Form: Overstriding detected (High Braking Force)")
            rehab_plan.append("Rx: Increase Cadence by 5% to fix landing")

        return {
            "user_id": user.id,
            "report_type": "B2B_ATHLETE_ADVANCED",
            "score": min(risk_score, 100), # 0-100 Risk Scale
            "alerts": alerts,
            "recommendations": rehab_plan
        }

    def _analyze_common_user(self, user, data):
        # === B2C LOGIC: Wellness & Lifestyle ===
        wellness_score = 100
        tips = []
        exercises = []

        # 1. Posture Check
        if data.mechanics and data.mechanics.head_forward_angle > 20:
            wellness_score -= 15
            tips.append("Detected 'Text Neck' posture.")
            exercises.append("Do Chin Tucks: 3 sets of 10")

        # 2. Pain Check
        if data.daily_stats and "Lower Back" in data.daily_stats.pain_areas:
            wellness_score -= 20
            tips.append("Lower back pain reported.")
            exercises.append("Do Cat-Cow Stretches")

        return {
            "user_id": user.id,
            "report_type": "B2C_WELLNESS_REPORT",
            "score": wellness_score, # 0-100 Health Scale
            "alerts": tips,
            "recommendations": exercises
        }