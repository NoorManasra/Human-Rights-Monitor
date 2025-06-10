from pymongo import MongoClient
from app.config import MONGO_URI, DB_NAME

#client = MongoClient(MONGO_URI)
#db = client[DB_NAME]
client = MongoClient("mongodb+srv://admin:nqdoEbgeEWkp9dFI@hrm-cluster.3yb5td1.mongodb.net/?retryWrites=true&w=majority&appName=HRM-Cluster")
db = client.human_rights_db
cases_collection = db.VictimsData
