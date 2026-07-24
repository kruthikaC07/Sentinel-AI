import re


CONTACTS = {
    "Medical": {
        "name": "Ambulance / Medical Emergency",
        "primary_number": "108",
        "alternate_number": "112",
        "department": "Medical",
        "message": "Call an ambulance immediately and keep the affected person stable until help arrives.",
    },
    "Ambulance": {
        "name": "Ambulance / Medical Emergency",
        "primary_number": "108",
        "alternate_number": "112",
        "department": "Medical",
        "message": "Call an ambulance immediately and keep the affected person stable until help arrives.",
    },
    "Fire": {
        "name": "Fire Department",
        "primary_number": "101",
        "alternate_number": "112",
        "department": "Fire",
        "message": "Report fire, smoke, gas cylinder fire, or rescue situations to the fire department.",
    },
    "Fire Department": {
        "name": "Fire Department",
        "primary_number": "101",
        "alternate_number": "112",
        "department": "Fire",
        "message": "Report fire, smoke, gas cylinder fire, or rescue situations to the fire department.",
    },
    "Police": {
        "name": "Police Emergency",
        "primary_number": "100",
        "alternate_number": "112",
        "department": "Police",
        "message": "Contact police for road accidents, crowd control, crime, traffic blockage, or public safety threats.",
    },
    "Disaster Response Team": {
        "name": "Disaster Response / National Emergency",
        "primary_number": "112",
        "alternate_number": "1078",
        "department": "Disaster Response",
        "message": "Use this for floods, building collapse, major rescue needs, or multi-agency emergencies.",
    },
    "Disaster Response": {
        "name": "Disaster Response / National Emergency",
        "primary_number": "112",
        "alternate_number": "1078",
        "department": "Disaster Response",
        "message": "Use this for floods, building collapse, major rescue needs, or multi-agency emergencies.",
    },
    "Electricity Department": {
        "name": "Electricity Emergency",
        "primary_number": "1912",
        "alternate_number": "112",
        "department": "Electricity Department",
        "message": "Report live wires, transformer fires, electrical hazards, and power-related emergencies.",
    },
    "Electrical Department": {
        "name": "Electrical Department",
        "primary_number": "1912",
        "alternate_number": "112",
        "department": "Electrical Department",
        "message": "Report streetlight failures, exposed wires, transformer issues, and local electrical hazards.",
    },
    "Sanitation Department": {
        "name": "Sanitation Department",
        "primary_number": "112",
        "alternate_number": "Local sanitation helpline",
        "department": "Sanitation Department",
        "message": "Report garbage overflow, waste accumulation, and sanitation hazards.",
    },
    "Water Department": {
        "name": "Water Department",
        "primary_number": "112",
        "alternate_number": "Local water board helpline",
        "department": "Water Department",
        "message": "Report water leakage, pipe damage, water logging, and public water supply issues.",
    },
    "Roads Department": {
        "name": "Roads Department",
        "primary_number": "112",
        "alternate_number": "Local roads helpline",
        "department": "Roads Department",
        "message": "Report potholes, road damage, fallen trees blocking roads, and unsafe road surfaces.",
    },
    "Municipal Services": {
        "name": "Municipal Services",
        "primary_number": "112",
        "alternate_number": "Local municipal helpline",
        "department": "Municipal Services",
        "message": "For garbage overflow, water leakage, potholes, drainage, and streetlight failures, the report is routed to registered municipal responders.",
    },
    "Women Support": {
        "name": "Women Support Emergency",
        "primary_number": "1091",
        "alternate_number": "112",
        "department": "Women Support",
        "message": "Use this for women safety threats, harassment, or urgent support requests.",
    },
    "Child Support": {
        "name": "Child Support Helpline",
        "primary_number": "1098",
        "alternate_number": "112",
        "department": "Child Support",
        "message": "Use this for child safety, missing child, abuse, or urgent child support needs.",
    },
    "Elderly Assistance": {
        "name": "Elderly Assistance",
        "primary_number": "14567",
        "alternate_number": "112",
        "department": "Elderly Assistance",
        "message": "Use this for elderly care, distress, or urgent senior citizen support requests.",
    },
    "Community Volunteer": {
        "name": "Community Volunteer Network",
        "primary_number": "112",
        "alternate_number": "Registered local volunteers",
        "department": "Community Volunteer",
        "message": "This report is routed to registered community volunteers for local assistance.",
    },
    "Gas Emergency": {
        "name": "Gas Leak Emergency",
        "primary_number": "1906",
        "alternate_number": "112",
        "department": "Fire",
        "message": "For gas leaks, avoid flames and switches, leave the area, and call gas emergency support.",
    },
}


RESPONDER_BY_KEYWORD = [
    (r"\b(garbage|trash|waste|overflow|sanitation)\b", "Sanitation Department"),
    (r"\b(water leak|leakage|pipe leak|water logging|water supply)\b", "Water Department"),
    (r"\b(pothole|road damage|broken road|fallen tree|road block|road surface)\b", "Roads Department"),
    (r"\b(streetlight|street light|broken light|lamp post)\b", "Electrical Department"),
    (r"\b(drain|drainage|sewage)\b", "Sanitation Department"),
    (r"\b(women|harassment|stalking|domestic|assault)\b", "Women Support"),
    (r"\b(child|children|missing child|abuse)\b", "Child Support"),
    (r"\b(elderly|senior citizen|old age|aged person)\b", "Elderly Assistance"),
    (r"\b(fire|flame|smoke|burn|burning|gas leak|cylinder|explosion)\b", "Fire"),
    (r"\b(heart|injur|bleed|medical|patient|unconscious|ambulance|stroke|fracture|wound)\b", "Medical"),
    (r"\b(accident|collision|crime|theft|violence|blocked road|traffic|fight)\b", "Police"),
    (r"\b(power|electric|wire|transformer|shock|short circuit)\b", "Electrical Department"),
    (r"\b(flood|collapse|earthquake|landslide|rescue|trapped|disaster)\b", "Disaster Response"),
]


def infer_responder(description: str, incident_type: str = "", recommended_responder: str = "") -> str:
    text = f"{description} {incident_type} {recommended_responder}".lower()
    for pattern, responder in RESPONDER_BY_KEYWORD:
        if re.search(pattern, text):
            return responder
    return recommended_responder if recommended_responder in CONTACTS else "Disaster Response"


def infer_severity(description: str, responder: str) -> str:
    text = description.lower()
    if re.search(r"\b(dead|death|trapped|unconscious|explosion|major fire|collapse|critical|severe bleeding)\b", text):
        return "Critical"
    if re.search(r"\b(fire|smoke|gas leak|accident|bleeding|violence|live wire|flood)\b", text):
        return "High"
    if responder in {"Sanitation Department", "Water Department", "Roads Department", "Electrical Department", "Municipal Services"}:
        return "Medium"
    return "Medium"


def incident_context(description: str, responder: str, is_emergency: bool = False) -> dict:
    text = description.lower()
    if is_emergency:
        return {
            "incident_category": "Emergency",
            "incident_type": "Emergency Alert",
            "priority_reason": "SOS alerts are treated as Critical because the citizen requested immediate assistance.",
            "ai_reason": [
                "The report was submitted through the SOS action.",
                "Location and timestamp should be reviewed immediately by responders.",
                "The incident may require rapid multi-agency coordination.",
            ],
            "impact_analysis": "Immediate risk to citizen safety until a responder accepts and verifies the situation.",
            "safety_recommendations": [
                "Move to the safest nearby visible location if possible.",
                "Keep your phone available for responder follow-up.",
                "Avoid confronting hazards or unsafe individuals.",
            ],
            "public_advisory": "Emergency activity may be underway nearby. Keep access routes clear and follow responder instructions.",
        }
    if "garbage" in text or "trash" in text or "waste" in text:
        return {
            "incident_category": "Community Issue",
            "incident_type": "Garbage Overflow",
            "priority_reason": "Medium priority because overflowing waste can create health hazards and block public access.",
            "ai_reason": [
                "Overflowing garbage may attract pests and create sanitation risks.",
                "The issue can worsen if it is near a school, market, or residential area.",
                "Sanitation Department cleanup is the most appropriate response.",
            ],
            "impact_analysis": "Possible odor, pests, blocked walkways, and local health concerns if not cleared promptly.",
            "safety_recommendations": [
                "Avoid walking close to the waste pile.",
                "Keep children away from the affected area.",
                "Use an alternate route until cleanup is completed.",
            ],
            "public_advisory": "Avoid contact with overflowing waste. Sanitation responders have been notified for cleanup and sanitation review.",
        }
    if "pothole" in text:
        return {
            "incident_category": "Community Issue",
            "incident_type": "Pothole",
            "priority_reason": "Medium priority because potholes can cause vehicle damage and traffic safety risks.",
            "ai_reason": [
                "Road surface damage can endanger two-wheelers and pedestrians.",
                "Traffic may slow or swerve around the damaged area.",
                "Roads Department repair is recommended.",
            ],
            "impact_analysis": "Risk of minor accidents, vehicle damage, and traffic disruption.",
            "safety_recommendations": [
                "Slow down near the affected road section.",
                "Avoid standing in traffic to photograph the pothole.",
                "Use another route if the road is narrow or poorly lit.",
            ],
            "public_advisory": "Use caution near the reported road damage and avoid sudden lane changes.",
        }
    if "water leak" in text or "leakage" in text or "water" in text:
        return {
            "incident_category": "Community Issue",
            "incident_type": "Water Leakage",
            "priority_reason": "Medium priority because water leakage can damage roads, waste water, and create slip risks.",
            "ai_reason": [
                "Standing or flowing water can make surfaces slippery.",
                "A leak can weaken roads or nearby structures over time.",
                "Water Department responders should inspect and isolate the source.",
            ],
            "impact_analysis": "Possible water wastage, slippery roads, minor flooding, and infrastructure damage.",
            "safety_recommendations": [
                "Avoid walking or driving through pooled water.",
                "Keep electrical devices away from the wet area.",
                "Report if the water level rises or blocks access.",
            ],
            "public_advisory": "Avoid the wet area and use alternate paths until municipal repair teams inspect the leak.",
        }
    if "streetlight" in text or "light" in text:
        return {
            "incident_category": "Community Issue",
            "incident_type": "Broken Streetlight",
            "priority_reason": "Low to Medium priority because poor lighting increases night-time safety risk.",
            "ai_reason": [
                "A failed streetlight can reduce visibility for pedestrians and drivers.",
                "The risk increases near junctions, schools, and residential lanes.",
                "Electrical Department maintenance is appropriate.",
            ],
            "impact_analysis": "Reduced visibility, increased risk of trips, and lower perceived public safety after dark.",
            "safety_recommendations": [
                "Avoid isolated dark stretches when possible.",
                "Use a better-lit route at night.",
                "Do not touch exposed wires or damaged poles.",
            ],
            "public_advisory": "Use caution in the affected area after dark and avoid touching electrical fixtures.",
        }
    if "drain" in text or "drainage" in text or "sewage" in text:
        return {
            "incident_category": "Community Issue",
            "incident_type": "Broken Drainage",
            "priority_reason": "Medium priority because drainage failures can create hygiene and flooding concerns.",
            "ai_reason": [
                "Blocked or damaged drainage can lead to stagnant water.",
                "Stagnant water increases mosquito and infection risk.",
                "Sanitation Department drainage repair is recommended.",
            ],
            "impact_analysis": "Possible foul smell, local flooding, mosquito breeding, and pedestrian inconvenience.",
            "safety_recommendations": [
                "Avoid stepping into open or overflowing drains.",
                "Keep children away from stagnant water.",
                "Use alternate routes until repair is complete.",
            ],
            "public_advisory": "Avoid open or overflowing drains and report any rapid water rise.",
        }
    if responder == "Fire":
        return {
            "incident_category": "Emergency",
            "incident_type": "Fire Incident",
            "priority_reason": "High priority because fire or smoke can spread quickly and threaten life and property.",
            "ai_reason": [
                "Fire/smoke keywords indicate a fast-moving hazard.",
                "Nearby people may require evacuation or rescue.",
                "Fire responders are the safest first response.",
            ],
            "impact_analysis": "Potential injury, property damage, smoke inhalation, and blocked access routes.",
            "safety_recommendations": [
                "Move away from smoke and heat immediately.",
                "Do not use elevators during a building fire.",
                "Keep access clear for fire responders.",
            ],
            "public_advisory": "Avoid the affected area and keep roads clear for fire response vehicles.",
        }
    if responder == "Medical":
        return {
            "incident_category": "Emergency",
            "incident_type": "Medical Emergency",
            "priority_reason": "High priority because injury or illness may need immediate medical support.",
            "ai_reason": [
                "The report indicates possible injury or health distress.",
                "Delay could worsen the citizen's condition.",
                "Medical responders are the recommended first response.",
            ],
            "impact_analysis": "Potential health deterioration if care is delayed.",
            "safety_recommendations": [
                "Keep the affected person still and comfortable.",
                "Do not move them unless the location is unsafe.",
                "Share clear location details with responders.",
            ],
            "public_advisory": "Give space to medical responders and avoid crowding around the affected person.",
        }
    return {
        "incident_category": "General",
        "incident_type": "Reported Incident",
        "priority_reason": "Medium priority because the report needs responder review and local assessment.",
        "ai_reason": [
            "The report describes a situation requiring field verification.",
            "The location and public impact should be reviewed by the assigned responder.",
            "The recommended responder type matches the incident context.",
        ],
        "impact_analysis": "Potential local inconvenience or safety risk until responders verify the situation.",
        "safety_recommendations": [
            "Avoid the affected area if it feels unsafe.",
            "Use alternate routes where possible.",
            "Update responders if the situation worsens.",
        ],
        "public_advisory": "Stay alert near the reported location and follow local responder instructions.",
    }


def contact_for_responder(responder: str) -> dict:
    if responder == "Gas Emergency":
        return CONTACTS["Gas Emergency"]
    return CONTACTS.get(responder, CONTACTS["Disaster Response"])


def enrich_analysis_with_contact(analysis: dict, description: str) -> dict:
    responder = infer_responder(description, analysis.get("incident_type", ""), analysis.get("recommended_responder", ""))
    if "gas" in f"{description} {analysis.get('incident_type', '')}".lower() and "leak" in f"{description} {analysis.get('incident_type', '')}".lower():
        contact = contact_for_responder("Gas Emergency")
        responder = contact["department"]
    else:
        contact = contact_for_responder(responder)

    return {
        **analysis,
        "recommended_responder": responder,
        "emergency_contact": contact,
    }


def notification_message(incident: dict) -> str:
    contact = contact_for_responder(incident.get("recommended_responder", ""))
    return f"New {incident.get('severity', 'priority')} incident for {contact['department']} at {incident.get('location', 'reported location')}."
