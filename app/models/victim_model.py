from pydantic import BaseModel, EmailStr
from typing import Optional, List

class RiskAssessment(BaseModel):
    level: str  # "low", "medium", "high"
    threats: List[str]
    protection_needed: bool

class VictimCreate(BaseModel):
    type: str = "victim"
    anonymous: bool
    demographics: dict
    contact_info: Optional[dict]
    cases_involved: List[str]
    risk_assessment: RiskAssessment
    support_services: Optional[List[dict]] = []

class VictimResponse(VictimCreate):
    id: str
