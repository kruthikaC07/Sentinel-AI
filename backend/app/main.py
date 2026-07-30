import json
import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import psycopg
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from psycopg.types.json import Jsonb

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env", override=True)

from .ai import analyze_incident
from .auth import create_token, hash_password, require_role, verify_password, current_user
from .database import DatabaseNotConfigured, get_db, init_db, row_to_dict
from .emergency_contacts import contact_for_responder, notification_message

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Sentinel AI API", version="1.0.0")
default_origins = "http://localhost:5173,http://127.0.0.1:5173"
allowed_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGIN", default_origins).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.exception_handler(DatabaseNotConfigured)
async def database_config_exception_handler(request: Request, exc: DatabaseNotConfigured):
    logger.error(
        "Database configuration error on %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(psycopg.Error)
async def postgres_exception_handler(request: Request, exc: psycopg.Error):
    logger.error(
        "PostgreSQL error on %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(status_code=503, content={"detail": f"Supabase PostgreSQL error: {exc}"})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled backend error on %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(status_code=500, content={"detail": f"Backend error: {exc}"})


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    responder_type: Optional[str] = None
    location: Optional[str] = None
    availability_status: Optional[str] = "Available"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class StatusRequest(BaseModel):
    status: str


class SOSRequest(BaseModel):
    location: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    description: Optional[str] = "SOS emergency alert submitted by citizen."


def parse_incident(row):
    data = row_to_dict(row)
    if not data:
        return None
    data["ai_reason"] = _json_value(data.get("ai_reason"), [])
    data["safety_recommendations"] = _json_value(data.get("safety_recommendations"), [])
    data["emergency_contact"] = _json_value(data.get("emergency_contact"), {})
    if not data["emergency_contact"]:
        data["emergency_contact"] = contact_for_responder(data.get("recommended_responder", ""))
    data["public_id"] = f"SI-{1000 + data['id']}"
    data["assigned_to"] = data.get("recommended_responder") or "Pending Assignment"
    data["priority"] = data.get("severity", "Medium")
    data["is_emergency"] = bool(data.get("is_emergency"))
    data["estimated_response"] = _estimated_response(data.get("status", ""))
    data["image_url"] = f"/uploads/{Path(data['image_path']).name}" if data.get("image_path") else None
    data["audio_url"] = f"/uploads/{Path(data['audio_path']).name}" if data.get("audio_path") else None
    return data


def _json_value(value, fallback):
    if value is None or value == "":
        return fallback
    if isinstance(value, (dict, list)):
        return value
    return json.loads(value)


def placeholders(values) -> str:
    return ",".join("%s" for _ in values) or "%s"


def _estimated_response(status: str) -> str:
    if status in {"Waiting for Responder", "Reported", "Assigned"}:
        return "Pending Acceptance"
    if status == "Accepted":
        return "Responder accepted"
    if status == "In Progress":
        return "Responder in progress"
    if status == "Resolved":
        return "Completed"
    return "Pending Acceptance"


def save_upload(file: Optional[UploadFile], prefix: str) -> Optional[str]:
    if not file or not file.filename:
        return None
    safe_name = "".join(ch for ch in file.filename if ch.isalnum() or ch in ".-_").strip(".")
    target = UPLOAD_DIR / f"{prefix}-{safe_name}"
    with target.open("wb") as output:
        output.write(file.file.read())
    return str(target)


DEPARTMENT_ALIASES = {
    "Fire": ["Fire", "Fire Department"],
    "Fire Department": ["Fire", "Fire Department"],
    "Medical": ["Medical", "Ambulance", "Medical Department", "Health Department"],
    "Medical Department": ["Medical", "Ambulance", "Medical Department", "Health Department"],
    "Ambulance": ["Medical", "Ambulance", "Medical Department", "Health Department"],
    "Police": ["Police", "Police Department", "Traffic Police"],
    "Police Department": ["Police", "Police Department", "Traffic Police"],
    "Disaster Response": ["Disaster Response", "Disaster Response Team"],
    "Disaster Response Team": ["Disaster Response", "Disaster Response Team"],
    "Electrical Department": ["Electrical Department", "Electricity Department"],
    "Electricity Department": ["Electrical Department", "Electricity Department"],
    "Municipal Services": [
        "Municipal Services",
        "Sanitation Department",
        "Water Department",
        "Roads Department",
        "Electrical Department",
        "Electricity Department",
    ],
    "Sanitation Department": ["Sanitation Department", "Municipal Services"],
    "Water Department": ["Water Department", "Municipal Services"],
    "Roads Department": ["Roads Department", "Municipal Services"],
    "Women Support": ["Women Support"],
    "Child Support": ["Child Support"],
    "Elderly Assistance": ["Elderly Assistance"],
    "Community Volunteer": ["Community Volunteer"],
}


def normalize_department(department: str | None) -> str:
    return " ".join((department or "").strip().lower().split())


def department_aliases(department: str | None) -> list[str]:
    if not department:
        return []
    aliases = DEPARTMENT_ALIASES.get(department, [department])
    return list(dict.fromkeys([*aliases, department]))


def responder_departments_for(user: dict) -> list[str]:
    return department_aliases(user.get("responder_type"))


def responder_types_for_incident(recommended_responder: str) -> list[str]:
    return department_aliases(recommended_responder)


def departments_match(responder_type: str | None, incident_department: str | None) -> bool:
    responder_aliases = {normalize_department(item) for item in department_aliases(responder_type)}
    incident_aliases = {normalize_department(item) for item in department_aliases(incident_department)}
    return bool(responder_aliases.intersection(incident_aliases))


def available_responders(db):
    return db.execute(
        """
        SELECT id, responder_type FROM users
        WHERE role = 'Responder'
          AND COALESCE(NULLIF(availability_status, ''), 'Available') = 'Available'
        """
    ).fetchall()


def insert_assignment_if_missing(db, incident_id: int, responder_id: int, recommended_responder: str, status: str = "Waiting for Responder"):
    db.execute(
        """
        INSERT INTO responder_assignments (incident_id, responder_id, recommended_responder, status)
        SELECT %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM responder_assignments
            WHERE incident_id = %s AND responder_id = %s
        )
        """,
        (incident_id, responder_id, recommended_responder, status, incident_id, responder_id),
    )


def assign_matching_responders(db, incident_id: int, recommended_responder: str, is_emergency: bool):
    responders = available_responders(db)
    matched = [
        responder
        for responder in responders
        if is_emergency or departments_match(responder.get("responder_type"), recommended_responder)
    ]
    logger.info(
        "Routing incident %s to %s responder(s). department=%s emergency=%s",
        incident_id,
        len(matched),
        recommended_responder,
        is_emergency,
    )
    if not matched:
        logger.warning("No available responders matched incident %s for department %s", incident_id, recommended_responder)
    for responder in matched:
        insert_assignment_if_missing(
            db,
            incident_id,
            responder["id"],
            responder.get("responder_type") or recommended_responder,
        )


def ensure_assignment_coverage(db):
    incidents = db.execute(
        """
        SELECT id, recommended_responder, is_emergency
        FROM incidents
        WHERE status IN ('Waiting for Responder', 'Reported', 'Assigned', 'Accepted', 'In Progress')
        """
    ).fetchall()
    for incident in incidents:
        assign_matching_responders(
            db,
            incident["id"],
            incident.get("recommended_responder") or "Disaster Response",
            bool(incident.get("is_emergency")),
        )


def create_incident_record(
    user: dict,
    description: str,
    location: str,
    latitude: str | None = None,
    longitude: str | None = None,
    people_affected: str = "",
    image_path: str | None = None,
    audio_path: str | None = None,
    is_emergency: bool = False,
):
    analysis = analyze_incident(description, location, people_affected, image_path, audio_path, is_emergency=is_emergency)
    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO incidents (
                citizen_id, description, location, latitude, longitude, people_affected, image_path, audio_path,
                incident_category, incident_type, severity, confidence, priority_reason, ai_reason,
                ai_summary, impact_analysis, safety_recommendations, recommended_responder,
                responder_reason, emergency_contact, public_advisory, is_emergency, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                user["id"],
                description,
                location,
                latitude,
                longitude,
                people_affected,
                image_path,
                audio_path,
                analysis.get("incident_category", "Emergency" if is_emergency else "General"),
                analysis["incident_type"],
                analysis["severity"],
                int(analysis["confidence"]),
                analysis.get("priority_reason", ""),
                Jsonb(analysis["ai_reason"]),
                analysis["ai_summary"],
                analysis["impact_analysis"],
                Jsonb(analysis["safety_recommendations"]),
                analysis["recommended_responder"],
                analysis["responder_reason"],
                Jsonb(analysis["emergency_contact"]),
                analysis["public_advisory"],
                is_emergency,
                "Waiting for Responder",
            ),
        )
        incident_id = cursor.fetchone()["id"]
        assign_matching_responders(db, incident_id, analysis["recommended_responder"], is_emergency)
        return parse_incident(db.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,)).fetchone())


@app.on_event("startup")
def startup():
    try:
        init_db()
    except Exception:
        logger.exception("Database initialization failed. API will stay online, but database-backed routes will fail until DATABASE_URL/network access is fixed.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "Sentinel AI"}


@app.get("/health/db")
def database_health():
    print("=== HEALTH/DB ENDPOINT CALLED ===")
    print("DATABASE_URL:", os.getenv("DATABASE_URL"))
    try:
        init_db()
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        logger.exception("Database health check failed.")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {exc}") from exc


@app.post("/auth/register")
def register(payload: RegisterRequest):
    if payload.role not in {"Citizen", "Responder"}:
        raise HTTPException(status_code=400, detail="Role must be Citizen or Responder")
    with get_db() as db:
        existing = db.execute("SELECT id FROM users WHERE email = %s", (payload.email.lower(),)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
        cursor = db.execute(
            """
            INSERT INTO users (name, email, password_hash, role, responder_type, location, availability_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                payload.name.strip(),
                payload.email.lower(),
                hash_password(payload.password),
                payload.role,
                payload.responder_type.strip() if payload.role == "Responder" and payload.responder_type else None,
                payload.location,
                payload.availability_status or "Available" if payload.role == "Responder" else None,
            ),
        )
        user = {
            "id": cursor.fetchone()["id"],
            "name": payload.name.strip(),
            "email": payload.email.lower(),
            "role": payload.role,
            "responder_type": payload.responder_type.strip() if payload.role == "Responder" and payload.responder_type else None,
            "location": payload.location,
            "availability_status": payload.availability_status or "Available" if payload.role == "Responder" else None,
        }
        if payload.role == "Responder":
            ensure_assignment_coverage(db)
    return {"token": create_token(user), "user": user}


@app.post("/auth/login")
def login(payload: LoginRequest):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE email = %s", (payload.email.lower(),)).fetchone()
    if not row or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "role": row["role"],
        "responder_type": row["responder_type"],
        "location": row["location"],
        "availability_status": row["availability_status"],
    }
    return {"token": create_token(user), "user": user}


@app.get("/auth/me")
def me(user: dict = Depends(current_user)):
    return user


@app.post("/ai/analyze")
def analyze_only(
    description: str = Form(...),
    location: str = Form(...),
    people_affected: str = Form(""),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    user: dict = Depends(require_role("Citizen", "Responder")),
):
    image_path = save_upload(image, f"preview-image-{user['id']}") if image else None
    audio_path = save_upload(audio, f"preview-audio-{user['id']}") if audio else None
    return analyze_incident(description, location, people_affected, image_path, audio_path)


@app.post("/incidents")
def create_incident(
    description: str = Form(...),
    location: str = Form(...),
    latitude: str = Form(""),
    longitude: str = Form(""),
    people_affected: str = Form(""),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    user: dict = Depends(require_role("Citizen")),
):
    image_path = save_upload(image, f"incident-image-{user['id']}") if image else None
    audio_path = save_upload(audio, f"incident-audio-{user['id']}") if audio else None
    return create_incident_record(user, description, location, latitude or None, longitude or None, people_affected, image_path, audio_path)


@app.post("/incidents/sos")
def create_sos(payload: SOSRequest, user: dict = Depends(require_role("Citizen"))):
    if not payload.location.strip():
        raise HTTPException(status_code=400, detail="Location is required for SOS alerts")
    description = payload.description or "SOS emergency alert submitted by citizen."
    return create_incident_record(
        user,
        description,
        payload.location.strip(),
        payload.latitude,
        payload.longitude,
        "Unknown",
        is_emergency=True,
    )


@app.get("/incidents")
def list_incidents(user: dict = Depends(current_user)):
    severity_order = "CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END"
    with get_db() as db:
        if user["role"] == "Responder":
            ensure_assignment_coverage(db)
        if user["role"] == "Citizen":
            rows = db.execute(
                f"SELECT * FROM incidents ORDER BY is_emergency DESC, {severity_order}, created_at DESC",
            ).fetchall()
        else:
            if user.get("responder_type"):
                rows = db.execute(
                    f"""
                    SELECT i.* FROM incidents i
                    JOIN responder_assignments ra ON ra.incident_id = i.id
                    WHERE ra.responder_id = %s
                       OR i.is_emergency = TRUE
                    ORDER BY i.is_emergency DESC, {severity_order}, i.created_at DESC
                    """,
                    (user["id"],),
                ).fetchall()
            else:
                rows = db.execute(f"SELECT * FROM incidents ORDER BY is_emergency DESC, {severity_order}, created_at DESC").fetchall()
    return [parse_incident(row) for row in rows]


@app.get("/incidents/{incident_id}")
def incident_detail(incident_id: int, user: dict = Depends(current_user)):
    with get_db() as db:
        row = db.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,)).fetchone()
        assignment = row_to_dict(db.execute("SELECT * FROM responder_assignments WHERE incident_id = %s ORDER BY id DESC", (incident_id,)).fetchone())
    incident = parse_incident(row)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident["assignment"] = assignment
    incident["notification"] = notification_message(incident)
    incident["timeline"] = [
        {"label": "Reported", "time": incident["created_at"]},
        {"label": f"AI triaged as {incident['severity']}", "time": incident["created_at"]},
        {"label": incident["status"], "time": incident["updated_at"]},
    ]
    return incident


@app.patch("/incidents/{incident_id}/status")
def update_status(incident_id: int, payload: StatusRequest, user: dict = Depends(require_role("Responder"))):
    allowed = {"Waiting for Responder", "Assigned", "Accepted", "In Progress", "Resolved", "Rejected"}
    if payload.status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status")
    with get_db() as db:
        db.execute(
            "UPDATE incidents SET status = %s, updated_at = NOW() WHERE id = %s",
            (payload.status, incident_id),
        )
        assignment_cursor = db.execute(
            "UPDATE responder_assignments SET status = %s, responder_id = COALESCE(responder_id, %s), updated_at = NOW() WHERE incident_id = %s",
            (payload.status, user["id"], incident_id),
        )
        if assignment_cursor.rowcount == 0:
            incident = row_to_dict(db.execute("SELECT recommended_responder FROM incidents WHERE id = %s", (incident_id,)).fetchone())
            if incident:
                db.execute(
                    """
                    INSERT INTO responder_assignments (incident_id, responder_id, recommended_responder, status)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (incident_id, user["id"], incident["recommended_responder"] or user.get("responder_type") or "Responder", payload.status),
                )
    return {"status": payload.status}

@app.post("/responders/assign/{incident_id}")
def assign_responder(
    incident_id: int,
    user: dict = Depends(require_role("Responder"))
):
    with get_db() as db:

        incident = row_to_dict(
            db.execute(
                "SELECT * FROM incidents WHERE id = %s",
                (incident_id,)
            ).fetchone()
        )

        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")

        existing = db.execute(
            """
            SELECT id
            FROM responder_assignments
            WHERE incident_id = %s
              AND responder_id = %s
            """,
            (incident_id, user["id"])
        ).fetchone()

        if existing:
            db.execute(
                """
                UPDATE responder_assignments
                SET
                    status = 'Assigned',
                    updated_at = NOW()
                WHERE incident_id = %s
                  AND responder_id = %s
                """,
                (incident_id, user["id"])
            )

        else:
            db.execute(
                """
                INSERT INTO responder_assignments
                (
                    incident_id,
                    responder_id,
                    recommended_responder,
                    status
                )
                VALUES (%s, %s, %s, 'Assigned')
                """,
                (
                    incident_id,
                    user["id"],
                    incident["recommended_responder"] or "Disaster Response Team"
                )
            )

        db.execute(
            """
            UPDATE incidents
            SET
                status='Assigned',
                updated_at=NOW()
            WHERE id=%s
            """,
            (incident_id,)
        )

    return {
        "message": "Dispatch recommendation sent successfully.",
        "status": "Assigned"
    }

@app.get("/responders/assignments")
def responder_assignments(user: dict = Depends(require_role("Responder"))):
    with get_db() as db:
        ensure_assignment_coverage(db)
        rows = db.execute(
            """
            SELECT i.*, ra.status AS assignment_status, ra.assigned_at
            FROM responder_assignments ra
            JOIN incidents i ON i.id = ra.incident_id
            WHERE ra.responder_id = %s
            ORDER BY ra.assigned_at DESC
            """,
            (user["id"],),
        ).fetchall()
    return [parse_incident(row) for row in rows]


@app.get("/responders/notifications")
def responder_notifications(user: dict = Depends(require_role("Responder"))):
    severity_order = "CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END"
    with get_db() as db:
        ensure_assignment_coverage(db)
        if user.get("responder_type"):
            rows = db.execute(
    f"""
    SELECT i.*
    FROM incidents i
    WHERE (
        i.id IN (
            SELECT ra.incident_id
            FROM responder_assignments ra
            WHERE ra.responder_id = %s
        )
        OR i.is_emergency = TRUE
    )
    AND i.status IN (
        'Waiting for Responder',
        'Reported',
        'Assigned',
        'Accepted',
        'In Progress'
    )
    ORDER BY
        i.is_emergency DESC,
        {severity_order},
        i.created_at DESC
    """,
    (user["id"],),
).fetchall()
        else:
            rows = db.execute(
                f"""
                SELECT * FROM incidents
                WHERE status IN ('Waiting for Responder', 'Reported', 'Assigned', 'Accepted', 'In Progress')
                ORDER BY {severity_order}, created_at DESC
                """
            ).fetchall()
    incidents = [parse_incident(row) for row in rows]
    return [
        {
            "id": incident["id"],
            "message": notification_message(incident),
            "incident_type": incident["incident_type"],
            "severity": incident["severity"],
            "is_emergency": incident["is_emergency"],
            "location": incident["location"],
            "created_at": incident["created_at"],
        }
        for incident in incidents
    ]
