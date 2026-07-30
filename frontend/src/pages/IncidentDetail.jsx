import { CheckCircle2, Phone, Send, ShieldAlert, Siren } from "lucide-react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import BackButton from "../components/BackButton.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { API_URL, api } from "../services/api.js";
import { severityBadge } from "../utils/severity.js";

export default function IncidentDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [incident, setIncident] = useState(null);
  const [message, setMessage] = useState("");
  const [showDispatchModal, setShowDispatchModal] = useState(false);

  async function load() {
    setIncident(await api(`/incidents/${id}`));
  }

  useEffect(() => {
    load().catch(console.error);
  }, [id]);

  async function assign() {
    const response = await api(`/responders/assign/${id}`, { method: "POST" });
    setMessage(response.message);
    await load();
  }

  async function updateStatus(status) {
    await api(`/incidents/${id}/status`, { method: "PATCH", body: { status } });
    setMessage(`Incident marked ${status}`);
    await load();
  }

  if (!incident) return <main className="page">Loading incident...</main>;

  return (
    <main className="page">
      <BackButton />
      <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div>
          <p className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-red-600">
            {incident.is_emergency && <Siren size={18} />}
            {incident.is_emergency ? "Emergency alert" : "Incident details"}
          </p>
          <h1 className="mt-2 text-3xl font-bold text-navy-900">#{incident.public_id} · {incident.incident_type}</h1>
          <p className="mt-2 text-slate-600">{incident.location}</p>
        </div>
        <span className={`w-fit rounded-full px-4 py-2 text-sm font-bold ring-1 ${severityBadge(incident.severity)}`}>{incident.severity}</span>
      </div>

      {message && <p className="mb-5 rounded-lg bg-green-50 p-3 text-sm font-semibold text-green-700">{message}</p>}

      <section className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <div className="space-y-6">
          {incident.image_url && (
            <div className="panel overflow-hidden p-0">
              <img className="h-72 w-full object-cover" src={`${API_URL}${incident.image_url}`} alt="Incident evidence" />
            </div>
          )}
          <InfoPanel title="Incident Summary" content={incident.ai_summary} />
          <InfoPanel title="Citizen Description" content={incident.description} />
          <InfoPanel title="Priority Explanation" content={incident.priority_reason} />
          <InfoPanel title="Impact Analysis" content={incident.impact_analysis} />
          <ListPanel title="AI Reason Card" items={incident.ai_reason} />
          <ListPanel title="Safety Recommendations" items={incident.safety_recommendations} />
          <ContactPanel contact={incident.emergency_contact} />
          <PublicAdvisoryPanel incident={incident} />
        </div>
        <aside className="space-y-6">
          <div className="panel">
            <h2 className="flex items-center gap-2 text-lg font-bold text-navy-900"><ShieldAlert size={20} /> Triage</h2>
            <dl className="mt-4 space-y-3 text-sm">
              <Row label="Severity" value={incident.severity} />
              <Row label="Category" value={incident.incident_category} />
              <Row label="Confidence" value={`${incident.confidence}%`} />
              <Row label="Status" value={incident.status} />
              <Row label="Assigned To" value={incident.assigned_to} />
              <Row label="Estimated Response" value={incident.estimated_response} />
              {incident.latitude && incident.longitude && <Row label="Coordinates" value={`${incident.latitude}, ${incident.longitude}`} />}
              <Row label="Reported" value={new Date(incident.created_at).toLocaleString()} />
            </dl>
            <p className="mt-4 rounded-lg bg-navy-50 p-3 text-sm text-navy-900">{incident.responder_reason}</p>
            {user.role === "Responder" && (
              <div className="mt-5 space-y-3">
                <button
  className="primary-button w-full"
  onClick={() => setShowDispatchModal(true)}
>
  <Send size={18} />
  Dispatch Recommendation
</button>
                <div className="grid grid-cols-1 gap-2">
                  {["Accepted", "Rejected", "In Progress", "Resolved"].map((status) => (
                    <button key={status} className="secondary-button" onClick={() => updateStatus(status)}>
                      <CheckCircle2 size={17} />
                      {status}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
          <div className="panel">
            <h2 className="text-lg font-bold text-navy-900">Timeline</h2>
            <div className="mt-4 space-y-4">
              {incident.timeline.map((item) => (
                <div key={`${item.label}-${item.time}`} className="border-l-2 border-navy-100 pl-4">
                  <p className="font-semibold">{item.label}</p>
                  <p className="text-xs text-slate-500">{new Date(item.time).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
      {showDispatchModal && (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
    <div className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-2xl">

      <h2 className="text-2xl font-bold">
        Dispatch Recommendation
      </h2>

      <div className="mt-6 space-y-4">

        <div>
          <p className="text-sm text-slate-500">
            Recommended Department
          </p>
          <p className="font-bold text-lg">
            {incident.assigned_to}
          </p>
        </div>

        <div>
          <p className="text-sm text-slate-500">
            Priority
          </p>
          <p className="font-semibold">
            {incident.severity}
          </p>
        </div>

        <div>
          <p className="text-sm text-slate-500">
            AI Reason
          </p>
          <p>
            {incident.responder_reason}
          </p>
        </div>

      </div>

      <div className="mt-8 flex justify-end gap-3">

        <button
          className="secondary-button"
          onClick={() => setShowDispatchModal(false)}
        >
          Cancel
        </button>

        <button
          className="primary-button"
          onClick={async () => {
            await assign();
            setShowDispatchModal(false);
          }}
        >
          Assign Team
        </button>

      </div>

    </div>
  </div>
)}
    </main>
  );
}

function InfoPanel({ title, content }) {
  return <div className="panel"><h2 className="text-lg font-bold text-navy-900">{title}</h2><p className="mt-3 text-slate-700">{content}</p></div>;
}

function ListPanel({ title, items }) {
  return <div className="panel"><h2 className="text-lg font-bold text-navy-900">{title}</h2><ul className="mt-3 space-y-2">{items.map((item) => <li key={item} className="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">{item}</li>)}</ul></div>;
}

function PublicAdvisoryPanel({ incident }) {
  const advisory = parsePublicAdvisory(incident);
  return (
    <div className="panel">
      <h2 className="text-xl font-black text-navy-900">Public Advisory</h2>
      <div className="mt-5 grid gap-4">
        <section className="rounded-lg bg-navy-50 p-4">
          <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Location</p>
          <p className="mt-1 font-semibold text-navy-900">{advisory.location}</p>
        </section>
        <section>
          <h3 className="text-sm font-bold uppercase tracking-wide text-red-600">Incident Summary</h3>
          <p className="mt-2 leading-7 text-slate-700">{advisory.summary}</p>
        </section>
        <section>
          <h3 className="text-sm font-bold uppercase tracking-wide text-red-600">Guidance For Citizens</h3>
          <p className="mt-2 leading-7 text-slate-700">{advisory.guidance}</p>
        </section>
        <section>
          <h3 className="text-sm font-bold uppercase tracking-wide text-red-600">Immediate Precautions</h3>
          <ul className="mt-3 space-y-2">
            {advisory.precautions.map((item) => (
              <li key={item} className="rounded-lg border border-slate-200 bg-white p-3 text-sm leading-6 text-slate-700">{item}</li>
            ))}
          </ul>
        </section>
        <section className="rounded-lg border border-amber-100 bg-amber-50 p-4">
          <h3 className="text-sm font-bold uppercase tracking-wide text-amber-700">Priority</h3>
          <p className="mt-2 leading-7 text-amber-900"><b>{incident.severity}</b> - {advisory.priorityReason}</p>
        </section>
      </div>
    </div>
  );
}

function parsePublicAdvisory(incident) {
  const text = incident.public_advisory || "";
  const field = (name, nextNames = []) => {
    const endPattern = nextNames.length ? `(?=\\s(?:${nextNames.join("|")}):|$)` : "$";
    const match = text.match(new RegExp(`${name}:\\s*(.*?)${endPattern}`, "i"));
    return match?.[1]?.trim();
  };
  return {
    location: field("Location", ["Summary", "Public advisory", "Priority"]) || incident.location,
    summary: field("Summary", ["Public advisory", "Priority"]) || incident.ai_summary || incident.description,
    guidance: field("Public advisory", ["Priority"]) || text || "Follow responder instructions and avoid the affected area when possible.",
    priorityReason: field("Reason") || incident.priority_reason || "Responder review is required.",
    precautions: incident.safety_recommendations?.length
      ? incident.safety_recommendations
      : ["Avoid the affected area if possible.", "Keep access routes clear for responders.", "Share updated information if the situation changes."]
  };
}

function ContactPanel({ contact }) {
  if (!contact?.primary_number) return null;
  return (
    <div className="panel border-red-100 bg-red-50">
      <h2 className="flex items-center gap-2 text-lg font-bold text-red-700"><Phone size={20} /> Recommended Emergency Contact</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-[1fr_auto] sm:items-center">
        <div>
          <p className="text-xl font-black text-navy-900">{contact.name}</p>
          <p className="mt-2 text-sm font-medium text-slate-700">{contact.message}</p>
        </div>
        <div className="rounded-lg bg-white p-4 text-center shadow-sm">
          <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Call Now</p>
          <a className="mt-1 block text-3xl font-black text-red-700" href={`tel:${contact.primary_number}`}>{contact.primary_number}</a>
          <p className="mt-1 text-xs text-slate-500">Alt: {contact.alternate_number}</p>
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }) {
  return <div className="flex justify-between gap-4"><dt className="text-slate-500">{label}</dt><dd className="text-right font-bold text-navy-900">{value}</dd></div>;
}
