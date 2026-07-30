import { Ambulance, Droplets, Flame, HeartHandshake, Lightbulb, Megaphone, PlusCircle, ShieldAlert, Siren, Trash2, TreePine, Waves } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import IncidentCard from "../components/IncidentCard.jsx";
import StatCard from "../components/StatCard.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { api } from "../services/api.js";

export default function CitizenDashboard() {
  const { user } = useAuth();
  const [incidents, setIncidents] = useState([]);
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    api("/incidents").then(setIncidents).catch(console.error);
  }, []);

  const active = useMemo(() => incidents.filter((incident) => incident.status !== "Resolved"), [incidents]);
  const latest = incidents[0];
  const filteredIncidents = useMemo(
    () => incidents.filter((incident) => filter === "All" || incident.severity === filter || incident.status === filter),
    [incidents, filter]
  );
  const critical = incidents.filter((incident) => incident.severity === "Critical").length;
  const pending = incidents.filter((incident) => incident.status !== "Resolved").length;
  const resolved = incidents.filter((incident) => incident.status === "Resolved").length;

  return (
    <main className="page">
      
      <section className="hero-panel grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-navy-100">Citizen dashboard</p>
          <h1 className="mt-3 text-4xl font-black">Welcome, {user.name}</h1>
          <p className="mt-3 max-w-2xl text-slate-200">
            Report emergencies or civic issues, let AI classify priority, and route the case to registered responders in seconds.
          </p>
          <Link to="/report" className="mt-6 inline-flex items-center gap-2 rounded-lg bg-red-600 px-5 py-3 font-bold text-white shadow-sm hover:bg-red-700">
            <PlusCircle size={20} />
            Report Incident
          </Link>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <StatCard label="Total Reports" value={incidents.length} />
          <StatCard label="Critical" value={critical} tone="red" />
          <StatCard label="Pending" value={pending} tone="amber" />
          <StatCard label="Resolved" value={resolved} tone="green" />
        </div>
      </section>

      <ServiceGrid />

      <section className="mt-8 grid gap-6 lg:grid-cols-[1fr_380px]">
        <div>
          <div className="section-heading">
            <h2>All Reports</h2>
            <div className="filter-row">
              {["All", "Critical", "High", "Medium", "Low", "Resolved"].map((item) => (
                <button key={item} className={`filter-chip ${filter === item ? "filter-chip-active" : ""}`} onClick={() => setFilter(item)}>{item}</button>
              ))}
            </div>
          </div>
          <div className="space-y-4">
            {filteredIncidents.length ? filteredIncidents.map((incident) => <IncidentCard key={incident.id} incident={incident} />) : <EmptyState text="No reports match this filter." />}
          </div>
        </div>
        <aside className="space-y-6">
          <div className="panel">
            <h2 className="text-lg font-bold text-navy-900">Current Incident Status</h2>
            {latest ? (
              <div className="soft-surface mt-4 rounded-lg p-4">
                <p className="font-semibold">{latest.incident_type}</p>
                <p className="mt-1 text-sm text-slate-600">{latest.location}</p>
                <p className="mt-3 text-sm">Status: <b>{latest.status}</b></p>
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-600">No active status yet.</p>
            )}
          </div>
          <div className="panel">
            <h2 className="flex items-center gap-2 text-lg font-bold text-navy-900">
              <Megaphone size={20} />
              Recent Public Advisories
            </h2>

            <div className="mt-4 space-y-4">
              {incidents.slice(0, 4).map((incident) => (
                <div
                  key={incident.id}
                  className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-semibold text-navy-900">
                        {incident.incident_type}
                      </h3>

                      <p className="mt-1 text-xs text-slate-500">
                        📍 {incident.location}
                      </p>
                    </div>

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-bold ${
                        incident.severity === "Critical"
                          ? "bg-red-100 text-red-700"
                          : incident.severity === "High"
                          ? "bg-orange-100 text-orange-700"
                          : incident.severity === "Medium"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-green-100 text-green-700"
                      }`}
                    >
                      {incident.severity}
                    </span>
                  </div>

                  <p className="mt-4 whitespace-pre-line text-sm leading-6 text-slate-700">
                    {incident.public_advisory}
                  </p>
                </div>
              ))}

              {!incidents.length && (
                <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-center text-slate-500">
                  No public advisories yet.
                </div>
              )}
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}

const emergencyServices = [
  { label: "Fire", icon: Flame, tone: "red" },
  { label: "Medical", icon: Ambulance, tone: "green" },
  { label: "Police", icon: ShieldAlert, tone: "blue" },
  { label: "Disaster", icon: Siren, tone: "amber" }
];

const communityIssues = [
  { label: "Garbage Overflow", icon: Trash2 },
  { label: "Water Leakage", icon: Droplets },
  { label: "Pothole", icon: Waves },
  { label: "Broken Streetlight", icon: Lightbulb },
  { label: "Broken Drainage", icon: HeartHandshake },
  { label: "Fallen Tree", icon: TreePine }
];

function ServiceGrid() {
  return (
    <section className="mt-8 grid gap-6 xl:grid-cols-2">
      <ServiceSection title="Emergency Services" items={emergencyServices} />
      <ServiceSection title="Community Issues" items={communityIssues} />
    </section>
  );
}

function ServiceSection({ title, items }) {
  return (
    <div className="panel">
      <div className="section-heading">
        <h2>{title}</h2>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {items.map(({ label, icon: Icon }) => (
          <Link key={label} to="/report" className="service-card">
            <span className="service-icon"><Icon size={22} /></span>
            <span>{label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}

function EmptyState({ text }) {
  return <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">{text}</div>;
}
// Dashboard UI update