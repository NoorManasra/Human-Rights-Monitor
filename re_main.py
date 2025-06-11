from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from uuid import uuid4
from pymongo import MongoClient
from bson import ObjectId
import os
import shutil
from datetime import datetime

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient("mongodb+srv://admin:nqdoEbgeEWkp9dFI@hrm-cluster.3yb5td1.mongodb.net/?retryWrites=true&w=majority&appName=HRM-Cluster")
db = client.human_rights_db
reports_collection = db.reports
evidence_collection = db.report_evidence

# Upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic Models

class Coordinates(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]

class Location(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    coordinates: Optional[Coordinates] = None

class IncidentDetails(BaseModel):
    date: datetime
    location: Location
    description: str
    violation_types: List[str]

class ReportIn(BaseModel):
    reporter_type: Optional[str] = Field(default="witness")  # could be reporter, victim, witness etc
    anonymous: bool = False
    contact_info: Optional[dict] = None  # e.g. {"email": "", "phone": "", "preferred_contact": ""}
    incident_details: IncidentDetails
    status: Optional[str] = Field(default="new")  # e.g. new, under review, resolved etc

# Helpers
def save_uploaded_files(report_id: str, files: List[UploadFile]) -> List[str]:
    saved_files = []
    for file in files:
        filename = f"{report_id}_{uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(filename)
    return saved_files

# API Endpoints

# 1. POST /reports/ - Submit a new incident report
@app.post("/reports/")
async def submit_report(
    reporter_type: str = Form("witness"),
    anonymous: bool = Form(False),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    preferred_contact: Optional[str] = Form(None),
    incident_date: str = Form(...),  # ISO date string
    country: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    longitude: Optional[float] = Form(None),
    latitude: Optional[float] = Form(None),
    description: str = Form(...),
    violation_types: List[str] = Form(...),  # multiple violation types allowed
    files: Optional[List[UploadFile]] = File(None)
):
    # Validate and parse date
    try:
        incident_date_obj = datetime.fromisoformat(incident_date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid incident_date format, use ISO format (YYYY-MM-DD).")

    # Compose location object
    coordinates = None
    if longitude is not None and latitude is not None:
        coordinates = {"type": "Point", "coordinates": [longitude, latitude]}
    location = {
        "country": country,
        "city": city,
        "coordinates": coordinates
    }

    report_id = str(ObjectId())

    report_doc = {
        "report_id": report_id,
        "reporter_type": reporter_type,
        "anonymous": anonymous,
        "contact_info": {
            "email": email or "",
            "phone": phone or "",
            "preferred_contact": preferred_contact or ""
        },
        "incident_details": {
            "date": incident_date_obj,
            "location": location,
            "description": description,
            "violation_types": violation_types
        },
        "status": "new",
        "created_at": datetime.utcnow(),
    }

    # Insert report document
    reports_collection.insert_one(report_doc)

    # Handle media files
    media_files = []
    if files:
        saved_filenames = save_uploaded_files(report_id, files)
        for filename in saved_filenames:
            evidence_doc = {
                "report_id": report_id,
                "filename": filename,
                "uploaded_at": datetime.utcnow()
            }
            evidence_collection.insert_one(evidence_doc)
            media_files.append(filename)

    return {"message": "Report submitted successfully", "report_id": report_id, "media_files": media_files}

# 2. GET /reports/ - List reports with optional filters
@app.get("/reports/")
def get_reports(
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    country: Optional[str] = Query(None)
):
    query = {}

    if status:
        query["status"] = status

    if start_date or end_date:
        date_filter = {}
        if start_date:
            try:
                date_filter["$gte"] = datetime.fromisoformat(start_date)
            except:
                raise HTTPException(status_code=400, detail="Invalid start_date format")
        if end_date:
            try:
                date_filter["$lte"] = datetime.fromisoformat(end_date)
            except:
                raise HTTPException(status_code=400, detail="Invalid end_date format")
        query["incident_details.date"] = date_filter

    if city:
        query["incident_details.location.city"] = city

    if country:
        query["incident_details.location.country"] = country

    reports = []
    for doc in reports_collection.find(query).sort("incident_details.date", -1):
        doc["id"] = doc["report_id"]
        # Fetch associated media files
        media = list(evidence_collection.find({"report_id": doc["report_id"]}))
        doc["media_files"] = [item["filename"] for item in media]
        # Convert datetime fields to ISO string for JSON serialization
        doc["incident_details"]["date"] = doc["incident_details"]["date"].isoformat()
        doc["created_at"] = doc["created_at"].isoformat()
        reports.append(doc)

    return reports

# 3. PATCH /reports/{report_id} - Update report status
@app.patch("/reports/{report_id}")
def update_report_status(report_id: str = Path(...), new_status: str = Form(...)):
    result = reports_collection.update_one(
        {"report_id": report_id},
        {"$set": {"status": new_status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Status updated successfully"}

# 4. GET /reports/analytics - Count reports by violation type
@app.get("/reports/analytics")
def reports_analytics():
    pipeline = [
        {"$unwind": "$incident_details.violation_types"},
        {"$group": {
            "_id": "$incident_details.violation_types",
            "count": {"$sum": 1}
        }}
    ]
    result = list(reports_collection.aggregate(pipeline))
    analytics = {item["_id"]: item["count"] for item in result}
    return analytics

# 5. GET media file by filename
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
