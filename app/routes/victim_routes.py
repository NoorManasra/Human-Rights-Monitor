from fastapi import APIRouter, Depends
from app.controllers.victim_controller import (
    create_victim_entry,
    get_victim_by_id,
    update_risk_level,
    list_victims_by_case
)
from app.models.victim_model import VictimCreate, RiskAssessment
from app.auth.auth_utils import get_current_user, require_admin

router = APIRouter()

@router.post("/")
def create_victim(victim: VictimCreate, user=Depends(get_current_user)):
    return create_victim_entry(victim)

@router.get("/{victim_id}")
def get_victim(victim_id: str, user=Depends(require_admin)):
    return get_victim_by_id(victim_id)

@router.patch("/{victim_id}")
def update_risk(victim_id: str, risk: RiskAssessment, user=Depends(get_current_user)):
    return update_risk_level(victim_id, risk, updated_by=user.username)

@router.get("/case/{case_id}")
def get_victims_for_case(case_id: str, user=Depends(get_current_user)):
    return list_victims_by_case(case_id)
