# reading.py
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
import random
import os
import sys

# Use environment variable if set, otherwise default to local mongo
MONGO_URI = os.getenv("mongodb+srv://vaishnavipithal_db_user:vaishnavi123@cluster0.1qcsetk.mongodb.net/?appName=Cluster0", "mongodb://localhost:27017")

try:
    client = MongoClient("mongodb+srv://vaishnavipithal_db_user:vaishnavi123@cluster0.1qcsetk.mongodb.net/?appName=Cluster0")
    # quick ping to confirm connection
    client.admin.command("ping")
except Exception as e:
    print("ERROR: Could not connect to MongoDB.")
    print("Tried URI:", MONGO_URI)
    print("Exception:", e)
    sys.exit(1)

db = client.smart_irrigation
readings = db.sensor_readings

# create 30 fake readings
for i in range(30):
    t = datetime.now(timezone.utc) - timedelta(minutes=10 * i)
    readings.insert_one({
        "timestamp": t.isoformat(),
        "s1": random.randint(20, 80),
        "s2": random.randint(20, 80),
        "s3": random.randint(20, 80)
    })

print("Seeded 30 readings into", readings.full_name)
