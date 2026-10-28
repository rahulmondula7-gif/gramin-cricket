import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
app = FastAPI(title="Gramin Cricket API", version="1.0.0", description="Rural cricket team registration and waiting list")
origins = [x.strip() for x in os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500,http://localhost:5500").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST", "PATCH", "OPTIONS"], allow_headers=["*"])

url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
db: Optional[Client] = create_client(url, key) if url and key and "YOUR_PROJECT" not in url and "YOUR_SUPABASE" not in key else None

class TeamRegistration(BaseModel):
    team_name: str = Field(min_length=2, max_length=100)
    village: str = Field(min_length=2, max_length=100)
    captain_name: str = Field(min_length=2, max_length=100)
    mobile: str = Field(min_length=10, max_length=15)
    manager_name: str = Field(default="", max_length=100)

    @field_validator("mobile")
    @classmethod
    def valid_mobile(cls, v):
        digits = ''.join(c for c in v if c.isdigit())
        if len(digits) != 10:
            raise ValueError("Enter a valid 10-digit mobile number")
        return digits


def database():
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not configured. Add SUPABASE_URL and SUPABASE_KEY to backend/.env")
    return db

@app.get("/api/health")
def health():
    return {"status": "ok", "database_configured": db is not None, "service": "Gramin Cricket"}

@app.post("/api/teams", status_code=201)
def register_team(team: TeamRegistration):
    client = database()
    # Prevent accidental duplicate team registrations within this tournament.
    existing = client.table("teams").select("id,team_name,status").ilike("team_name", team.team_name.strip()).limit(1).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="This team name is already registered. Contact the organizer if this is your team.")
    counts = client.table("teams").select("id", count="exact").eq("status", "confirmed").execute()
    capacity_row = client.table("tournament_settings").select("max_teams").eq("id", 1).single().execute()
    max_teams = int(capacity_row.data["max_teams"])
    status = "confirmed" if (counts.count or 0) < max_teams else "waiting"
    result = client.table("teams").insert({
        "team_name": team.team_name.strip(), "village": team.village.strip(),
        "captain_name": team.captain_name.strip(), "mobile": team.mobile,
        "manager_name": team.manager_name.strip() or None, "status": status
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Registration was not saved. Please try again.")
    return {"message": "Registration submitted successfully", "team": result.data[0]}

@app.get("/api/teams")
def list_teams(status: Optional[str] = Query(default=None, pattern="^(confirmed|waiting)$")):
    client = database()
    q = client.table("teams").select("id,team_name,village,captain_name,mobile,manager_name,status,created_at").order("created_at")
    if status:
        q = q.eq("status", status)
    result = q.execute()
    return {"teams": result.data, "count": len(result.data)}

@app.patch("/api/teams/{team_id}/status")
def update_status(team_id: int, status: str = Query(..., pattern="^(confirmed|waiting)$")):
    client = database()
    result = client.table("teams").update({"status": status}).eq("id", team_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": "Team status updated", "team": result.data[0]}
