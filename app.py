from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime,timezone
from bson import ObjectId
import certifi
import ssl

app = Flask(__name__)
CORS(app)

# Replace with your MongoDB URI
# Disable SSL certificate verification for development (use with caution)
client = MongoClient(
    "mongodb+srv://vaishnavipithal_db_user:vaishnavi123@cluster0.1qcsetk.mongodb.net/?appName=Cluster0",
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000
)

db = client.smart_irrigation
state_col = db.system_state
readings_col = db.sensor_readings
try:
    client.admin.command("ping")
    print("MongoDB ping OK")
except Exception as e:
    print("MongoDB ping failed:", repr(e))


def serialize_state(doc):
    if not doc:
        return {}
    result = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            result[k] = str(v)
        elif isinstance(v, datetime):
            # convert to ISO 8601 string (UTC)
            result[k] = v.astimezone(timezone.utc).isoformat()
        else:
            result[k] = v
    return result
# Ensure one state document
def get_state_doc():
    doc = state_col.find_one()
    if not doc:
        doc = {
            "motor_status": False,
            "current_mode": "Auto",
            "last_command_time": None,
            "last_reading_time": None,
            "valve_1_status": False,
            "valve_2_status": False,
            "valve_3_status": False,
            "s1_limit_low": 20,
            "s1_limit_high": 80,
            "s2_limit_low": 20,
            "s2_limit_high": 80,
            "s3_limit_low": 20,
            "s3_limit_high": 80
        }
        state_col.insert_one(doc)
        doc = state_col.find_one()
    return doc

@app.route("/api/status", methods=["GET"])
def status():
    try:
        doc = get_state_doc()  # your existing helper
        doc_serializable = serialize_state(doc)
        return jsonify(doc_serializable)
    except Exception as e:
        # helpful debug output in logs; returns an error message to client
        app.logger.exception("Error in /api/status")
        return jsonify({"error": "internal server error", "detail": str(e)}), 500

@app.route("/api/readings", methods=["GET"])
def readings():
    last50 = list(readings_col.find().sort("timestamp",-1).limit(50))
    for r in last50:
        r["_id"] = str(r["_id"])
    return jsonify(last50)

@app.route("/api/command", methods=["POST"])
def command():
    payload = request.get_json()
    payload["last_command_time"] = datetime.utcnow().isoformat()
    state_col.update_one({}, {"$set": payload}, upsert=True)
    return jsonify({"status":"ok","applied":payload})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
