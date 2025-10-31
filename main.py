from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Health Monitor API (PostgreSQL) running 🚀"}

@app.post("/api/v1/vitals")
async def post_vitals(request: Request):
    data = await request.json()
    hr = data.get("heartRate")
    spo2 = data.get("spo2")
    temp = data.get("temperature")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO vitals (heart_rate, spo2, temperature) VALUES (%s, %s, %s)",
        (hr, spo2, temp)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"success": True, "message": "Vitals saved"}

@app.post("/api/v1/ecg")
async def post_ecg(request: Request):
    data = await request.json()
    user_id = data.get("user_id", 1)
    ts = datetime.fromtimestamp(data.get("timestamp_start"))
    rate = data.get("sampling_rate")
    samples = str(data.get("ecg_data"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ecg_samples (user_id, timestamp_start, sampling_rate, samples) VALUES (%s, %s, %s, %s)",
        (user_id, ts, rate, samples)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"success": True, "message": "ECG data saved"}

@app.get("/api/v1/vitals")
def get_vitals():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vitals ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    
    vitals_list = []
    for row in rows:
        vitals_list.append({
            "id": row[0],
            "heart_rate": row[1],
            "spo2": row[2],
            "temperature": row[3],
            "timestamp": row[4]
        })
        
    cur.close()
    conn.close()
    return vitals_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
