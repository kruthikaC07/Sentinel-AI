import { ArrowRight, CheckCircle2, LocateFixed, RotateCcw, UploadCloud } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import BackButton from "../components/BackButton.jsx";
import { api } from "../services/api.js";
import { getReadableLocation } from "../utils/location.js";

export default function ReportIncident() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [completedIncident, setCompletedIncident] = useState(null);
  const [error, setError] = useState("");
  const [locating, setLocating] = useState(false);
  const [form, setForm] = useState({
    description: "",
    location: "",
    latitude: "",
    longitude: "",
    people_affected: "",
    image: null,
    audio: null
  });

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setCompletedIncident(null);
    setError("");
    const body = new FormData();
    body.append("description", form.description);
    body.append("location", form.location);
    body.append("latitude", form.latitude);
    body.append("longitude", form.longitude);
    body.append("people_affected", form.people_affected);
    if (form.image) body.append("image", form.image);
    if (form.audio) body.append("audio", form.audio);

    try {
      const incident = await api("/incidents", { method: "POST", body });
      setCompletedIncident(incident);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  function resetForm() {
    setCompletedIncident(null);
    setForm({ description: "", location: "", latitude: "", longitude: "", people_affected: "", image: null, audio: null });
  }

  async function fillCurrentLocation() {
    setLocating(true);
    setError("");
    const result = await getReadableLocation();
    if (result) {
      setForm((value) => ({
        ...value,
        location: result.address,
        latitude: result.latitude,
        longitude: result.longitude
      }));
    }
    setLocating(false);
  }

  return (
    <main className="page max-w-5xl">
      <BackButton />
      <div className="section-heading">
        <div>
          <p className="text-sm font-bold uppercase tracking-wide text-red-600">AI incident submission</p>
          <h1>Submit Report and Notify Responders</h1>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        {completedIncident ? (
          <CompletionCard incident={completedIncident} onOpen={() => navigate(`/incidents/${completedIncident.id}`)} onReset={resetForm} />
        ) : (
          <form onSubmit={submit} className="panel space-y-5">
            {error && <p className="alert">{error}</p>}
            <label className="field-label">Text Description<textarea className="field min-h-36" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required /></label>
            <label className="field-label">
              Incident Location
              <div className="flex gap-2">
                <input className="field" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value, latitude: "", longitude: "" })} placeholder="Area, street, landmark, or coordinates" required />
                <button className="icon-button shrink-0" type="button" onClick={fillCurrentLocation} title="Use current location" aria-label="Use current location">
                  <LocateFixed size={18} className={locating ? "animate-pulse" : ""} />
                </button>
              </div>
              {form.latitude && form.longitude && <span className="text-xs font-semibold text-slate-500">Coordinates saved: {form.latitude}, {form.longitude}</span>}
            </label>
            <label className="field-label">People Affected<input className="field" value={form.people_affected} onChange={(e) => setForm({ ...form, people_affected: e.target.value })} placeholder="Optional" /></label>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="upload-box">
                <UploadCloud size={24} />
                <span>{form.image ? form.image.name : "Upload Image"}</span>
                <input type="file" accept="image/*" className="sr-only" onChange={(e) => setForm({ ...form, image: e.target.files[0] })} />
              </label>
              <label className="upload-box">
                <UploadCloud size={24} />
                <span>{form.audio ? form.audio.name : "Audio Upload (optional)"}</span>
                <input type="file" accept="audio/*" className="sr-only" onChange={(e) => setForm({ ...form, audio: e.target.files[0] })} />
              </label>
            </div>
            <button className="primary-button" disabled={loading}>{loading ? "Processing Report..." : "Submit Report"}</button>
          </form>
        )}
        <aside><IntakeGuide /></aside>
      </div>
    </main>
  );
}

function CompletionCard({ incident, onOpen, onReset }) {
  return (
    <section className="panel border-green-100 bg-green-50">
      <div className="flex items-center gap-3">
        <CheckCircle2 size={34} className="text-green-600" />
        <div>
          <p className="text-sm font-bold uppercase tracking-wide text-green-700">Report submitted</p>
          <h2 className="text-2xl font-black text-navy-900">Incident #{incident.public_id}</h2>
        </div>
      </div>

      <div className="mt-6 rounded-lg bg-white p-4 text-sm text-slate-700 shadow-sm">
        <p className="font-semibold text-navy-900">{incident.ai_summary}</p>
        <p className="mt-2">Your report was saved and matching responders have been notified.</p>
      </div>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button className="primary-button" onClick={onOpen}><ArrowRight size={18} /> Open Incident</button>
        <button className="secondary-button" onClick={onReset}><RotateCcw size={17} /> Submit Another</button>
      </div>
    </section>
  );
}

function IntakeGuide() {
  return (
    <div className="panel">
      <h2 className="text-lg font-bold text-navy-900">AI Review</h2>
      <div className="mt-4 space-y-3 text-sm text-slate-600">
        <p>Sentinel AI analyzes your description, evidence, location, urgency, and likely public impact.</p>
        <p>After submission, the report is routed directly to matching responders.</p>
        <p className="font-bold text-red-600">For immediate danger, use the SOS button in the header.</p>
      </div>
    </div>
  );
}
