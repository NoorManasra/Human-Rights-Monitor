from bson import ObjectId
from datetime import datetime
from app.models.victim_model import VictimCreate, RiskAssessment
from app.database.connection import db

victims_collection = db["victims"]
risk_log_collection = db["victim_risk_assessments"]

def create_victim_entry(victim: VictimCreate):
    victim_data = victim.dict()
    victim_data["created_at"] = datetime.utcnow()
    victim_data["updated_at"] = datetime.utcnow()
    result = victims_collection.insert_one(victim_data)
    return {"id": str(result.inserted_id)}

def get_victim_by_id(victim_id: str):
    victim = victims_collection.find_one({"_id": ObjectId(victim_id)})
    if not victim:
        return {"error": "Victim not found"}
    victim["id"] = str(victim["_id"])
    return victim

def update_risk_level(victim_id: str, risk: RiskAssessment, updated_by="system"):
    update_data = {
        "$set": {
            "risk_assessment": risk.dict(),
            "updated_at": datetime.utcnow()
        }
    }
    victims_collection.update_one({"_id": ObjectId(victim_id)}, update_data)

    risk_log = {
        "victim_id": victim_id,
        "level": risk.level,
        "threats": risk.threats,
        "protection_needed": risk.protection_needed,
        "updated_at": datetime.utcnow(),
        "updated_by": updated_by
    }
    risk_log_collection.insert_one(risk_log)
    return {"msg": "Risk level updated and logged"}

def list_victims_by_case(case_id: str):
    victims = victims_collection.find({"cases_involved": case_id})
    result = []
    for v in victims:
        v["id"] = str(v["_id"])
        result.append(v)
    return result
