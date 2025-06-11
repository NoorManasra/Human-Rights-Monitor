from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from pymongo import MongoClient
from bson import ObjectId
import os
import shutil

app = FastAPI()

# Enable connection from Streamlit (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://admin:nqdoEbgeEWkp9dFI@hrm-cluster.3yb5td1.mongodb.net/?retryWrites=true&w=majority&appName=HRM-Cluster")
db = client.human_rights_db
reports_collection = db.reports

# Directory for uploaded media
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic model for structure (optional)
class Report(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    anonymous: bool = False
    status: str = "Under Review"
    media_files: List[str] = []

# Submit a new report
@app.post("/submit_report/")
async def submit_report(
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(None),
    anonymous: bool = Form(False),
    files: Optional[List[UploadFile]] = File(None)
):
    report_id = str(uuid4())
    media_paths = []

    if files:
        for file in files:
            filename = f"{report_id}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            media_paths.append(file_path)

    report_data = {
        "title": title,
        "description": description,
        "location": location,
        "anonymous": anonymous,
        "status": "Under Review",
        "media_files": media_paths
    }

    result = reports_collection.insert_one(report_data)
    return {"message": "Report submitted successfully", "id": str(result.inserted_id)}

# Get all reports
@app.get("/reports/")
def get_reports():
    reports = []
    for report in reports_collection.find():
        report["id"] = str(report["_id"])
        del report["_id"]
        reports.append(report)
    return reports

# Get a specific report
@app.get("/report/{report_id}")
def get_report(report_id: str):
    report = reports_collection.find_one({"_id": ObjectId(report_id)})
    if report:
        report["id"] = str(report["_id"])
        del report["_id"]
        return report
    return {"error": "Report not found"}

# Download a media file
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    return FileResponse(file_path)

# Update report status
@app.post("/update_status/")
def update_status(report_id: str, new_status: str):
    result = reports_collection.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": {"status": new_status}}
    )
    if result.matched_count == 0:
        return {"error": "Report not found"}
    return {"message": "Status updated successfully"}
