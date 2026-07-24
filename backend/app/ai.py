import base64
import json
import logging
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from .emergency_contacts import enrich_analysis_with_contact, incident_context, infer_responder, infer_severity


load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

logger = logging.getLogger(__name__)
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

VALID_DEPARTMENTS = {
    "Fire",
    "Police",
    "Medical",
    "Disaster Response",
    "Sanitation Department",
    "Water Department",
    "Roads Department",
    "Electrical Department",
    "Women Support",
    "Child Support",
    "Elderly Assistance",
    "Community Volunteer",
}
VALID_SEVERITIES = {"Low", "Medium", "High", "Critical"}

DEFAULT_ANALYSIS = {
    "incident_type": "Emergency Incident",
    "incident_category": "General",
    "severity": "High",
    "confidence": 82,
    "priority_reason": "The incident requires responder review based on the submitted description.",
    "ai_reason": [
        "The report describes a potentially urgent situation.",
        "The location may require fast responder coordination.",
        "More evidence should be reviewed by the assigned team.",
    ],
    "ai_summary": "A citizen reported an emergency that needs responder review and possible dispatch.",
    "impact_analysis": "Potential risk to nearby people, property, and access routes until responders assess the scene.",
    "safety_recommendations": [
        "Move to a safe distance from the incident area.",
        "Avoid blocking emergency access routes.",
        "Follow official responder instructions.",
    ],
    "recommended_responder": "Disaster Response",
    "responder_reason": "The incident needs coordinated triage until the exact responder category is confirmed.",
    "public_advisory": "Avoid the affected area and allow emergency teams to access the location.",
    "emergency_contact": {},
}


def _clean_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    if "{" in cleaned and "}" in cleaned:
        cleaned = cleaned[cleaned.find("{") : cleaned.rfind("}") + 1]
    return json.loads(cleaned)


def _gemini_error_message(exc: Exception) -> str:
    if isinstance(exc, HTTPError):
        body = exc.read().decode("utf-8", errors="replace")
        return f"Gemini HTTP {exc.code}: {body}"
    if isinstance(exc, URLError):
        return f"Gemini connection error: {exc.reason}"
    return str(exc)


def _configured_gemini_key() -> str | None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key.lower() in {"none", "null", "undefined"} or api_key in {"your_google_ai_studio_key", "replace-with-your-gemini-key", "YOUR_GEMINI_API_KEY"}:
        return None
    return api_key


def _gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip() or "gemini-3.5-flash"


def _as_list(value, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return fallback


def _normalize_analysis(analysis: dict, description: str, is_emergency: bool) -> dict:
    responder = analysis.get("recommended_responder") or infer_responder(description)
    if responder not in VALID_DEPARTMENTS:
        responder = infer_responder(description)

    severity = analysis.get("severity") or infer_severity(description, responder)
    if severity not in VALID_SEVERITIES:
        severity = infer_severity(description, responder)
    if is_emergency:
        severity = "Critical"
        analysis["incident_category"] = "Emergency"

    try:
        confidence = int(analysis.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 82

    return {
        **analysis,
        "recommended_responder": responder,
        "severity": severity,
        "confidence": max(0, min(confidence, 100)),
        "ai_reason": _as_list(analysis.get("ai_reason"), DEFAULT_ANALYSIS["ai_reason"]),
        "safety_recommendations": _as_list(
            analysis.get("safety_recommendations"),
            DEFAULT_ANALYSIS["safety_recommendations"],
        ),
    }


def _contextual_public_advisory(analysis: dict, location: str, description: str) -> str:
    summary = (analysis.get("ai_summary") or description).strip().rstrip(".")
    priority = analysis.get("severity", "Medium")
    reason = analysis.get(
        "priority_reason",
        "Responder review is required."
    )

    base = analysis.get(
        "public_advisory",
        "Avoid the affected area and follow responder instructions."
    )

    return f"""
{summary}

Public Advisory

{base}

Safety Tips
• Avoid the affected area.
• Keep children and pets away.
• Keep emergency routes clear.
• Follow official responder instructions.

Reason
{reason}
""".strip()

def _finalize_analysis(analysis: dict, description: str, location: str) -> dict:
    enriched = enrich_analysis_with_contact(analysis, description)
    enriched["public_advisory"] = _contextual_public_advisory(enriched, location, description)
    return enriched


def _image_part(path: Path) -> dict:
    return {
        "inline_data": {
            "mime_type": _mime_type(path),
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
    }


def _call_gemini(api_key: str, parts: list[dict]) -> dict:
    model_name = _gemini_model()
    url = f"{GEMINI_API_BASE}/{model_name}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseMimeType": "application/json",
        },
    }
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print("========== GEMINI ERROR ==========")
        print(_gemini_error_message(e))
        raise

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini returned no candidates: {data}")

    response_parts = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(part.get("text", "") for part in response_parts if part.get("text"))
    if not text.strip():
        raise RuntimeError(f"Gemini returned no text parts: {data}")
    return _clean_json(text)


def analyze_incident(
    description: str,
    location: str,
    people_affected: str = "",
    image_path: str | None = None,
    audio_path: str | None = None,
    is_emergency: bool = False,
) -> dict:
    api_key = _configured_gemini_key()
    if not api_key:
        logger.warning("Gemini fallback used because GEMINI_API_KEY is missing or still set to the placeholder value.")
        responder = infer_responder(description)
        context = incident_context(description, responder, is_emergency)
        analysis = {
            **DEFAULT_ANALYSIS,
            **context,
            "recommended_responder": responder,
            "severity": "Critical" if is_emergency else infer_severity(description, responder),
            "confidence": 96 if is_emergency else 88,
            "ai_summary": description.strip().capitalize(),
            "ai_provider": "local_fallback",
        }
        return _finalize_analysis(analysis, description, location)

    prompt = f"""
    You are Sentinel AI, an emergency decision intelligence assistant.
    Analyze this incident and respond as strict JSON only.

    Required JSON keys:
    incident_category, incident_type, severity, confidence, priority_reason, ai_reason, ai_summary, impact_analysis,
    safety_recommendations, recommended_responder, responder_reason, public_advisory.

    severity must be one of Low, Medium, High, Critical.
    recommended_responder must be one of Fire, Police, Medical, Disaster Response,
    Sanitation Department, Water Department, Roads Department, Electrical Department,
    Women Support, Child Support, Elderly Assistance, Community Volunteer.
    confidence must be an integer from 0 to 100.
    ai_reason and safety_recommendations must be arrays of short strings.
    priority_reason must explain briefly why the priority level was chosen.
    public_advisory must include practical citizen guidance, environmental/public impact if relevant,
    expected urgency, and temporary precautions.

    Description: {description}
    Location: {location}
    People affected: {people_affected or "Unknown"}
    Image uploaded: {"Yes" if image_path else "No"}
    Audio uploaded: {"Yes" if audio_path else "No"}
    SOS emergency alert: {"Yes" if is_emergency else "No"}
    """

    parts: list[dict] = [{"text": prompt}]
    if image_path:
        path = Path(image_path)
        if path.exists():
            parts.append(_image_part(path))

    try:
        last_error = None

        for attempt in range(3):
            try:
                analysis = _call_gemini(api_key, parts)

                analysis = _normalize_analysis(
                    {**DEFAULT_ANALYSIS, **analysis, "ai_provider": "gemini"},
                    description,
                    is_emergency,
                )

                return _finalize_analysis(
                    analysis,
                    description,
                    location,
                )

            except Exception as exc:
                last_error = exc

                # Retry only if Gemini is temporarily unavailable
                if "503" in _gemini_error_message(exc):
                    time.sleep(2 ** attempt)   # 1s → 2s → 4s
                    continue

                raise

        raise last_error

    except Exception as exc:
        logger.exception("Gemini failed after all retries.")
        
        responder = infer_responder(description)
        context = incident_context(description, responder, is_emergency)

        analysis = {
             **DEFAULT_ANALYSIS,
             **context,
             "recommended_responder": responder,
             "severity": "Critical" if is_emergency else infer_severity(description, responder),
             "confidence": 96 if is_emergency else 82,
             "ai_summary": description.strip().capitalize(),
             "ai_provider": "local_fallback",
        }

        return _finalize_analysis(
             analysis,
             description,
             location,
        )


def _mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".png"}:
        return "image/png"
    if suffix in {".webp"}:
        return "image/webp"
    return "image/jpeg"
