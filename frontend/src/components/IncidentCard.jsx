import { AlertTriangle, Clock, ImageIcon, MapPin, RadioTower, Siren } from "lucide-react";
import { Link } from "react-router-dom";
import { API_URL } from "../services/api.js";
import { severityBadge } from "../utils/severity.js";

export default function IncidentCard({ incident }) {
  return (
    <Link to={`/incidents/${incident.id}`} className={`incident-card block rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-command ${incident.is_emergency ? "emergency-card" : ""}`}>
      <div className="flex gap-4">
        <div className="incident-thumb">
          {incident.image_url ? <img src={`${API_URL}${incident.image_url}`} alt="" /> : <ImageIcon size={24} />}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-4">
            <div>
          <p className="flex items-center gap-2 text-sm font-semibold text-navy-900">
            {incident.is_emergency ? <Siren size={17} /> : <AlertTriangle size={17} />}
            {incident.is_emergency && <span className="emergency-label">Emergency</span>}
            {incident.incident_type}
          </p>
              <p className="mt-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-slate-500">
                <RadioTower size={14} />
                {incident.incident_category || "Incident"} · {incident.assigned_to || incident.recommended_responder}
              </p>
          <p className="mt-3 flex items-center gap-2 text-sm text-slate-600">
            <MapPin size={16} />
            {incident.location}
          </p>
              <p className="mt-3 line-clamp-2 text-sm text-slate-600">{incident.description}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-bold ring-1 ${severityBadge(incident.severity)}`}>
          {incident.severity}
        </span>
      </div>
      <div className="mt-5 grid gap-3 text-xs text-slate-500 sm:grid-cols-3">
        <span className="flex items-center gap-1">
          <Clock size={14} />
          {new Date(incident.created_at).toLocaleString()}
        </span>
        <span>Status: <b className="text-slate-700">{incident.status}</b></span>
        <span>Confidence: <b className="text-slate-700">{incident.confidence}%</b></span>
      </div>
        </div>
      </div>
    </Link>
  );
}
