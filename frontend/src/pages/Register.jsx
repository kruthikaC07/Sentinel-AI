import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "Citizen",
    responder_type: "Sanitation Department",
    location: "",
    availability_status: "Available"
  });
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      const user = await register(form);
      navigate(user.role === "Responder" ? "/responder" : "/citizen");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="screen-center px-4">
      <form onSubmit={submit} className="auth-panel">
        <div>
          <p className="text-sm font-bold uppercase tracking-wide text-red-600">New operator</p>
          <h1 className="mt-2 text-3xl font-bold text-navy-900">Create your Sentinel AI account</h1>
        </div>
        {error && <p className="alert">{error}</p>}
        <label className="field-label">Name<input className="field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></label>
        <label className="field-label">Email<input className="field" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></label>
        <label className="field-label">Password<input className="field" type="password" minLength="6" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required /></label>
        <label className="field-label">Location<input className="field" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="Area, city, landmark" required /></label>
        <div className="grid grid-cols-2 gap-3">
          {["Citizen", "Responder"].map((role) => (
            <button type="button" key={role} onClick={() => setForm({ ...form, role })} className={`segmented ${form.role === role ? "segmented-active" : ""}`}>{role}</button>
          ))}
        </div>
        {form.role === "Responder" && (
          <label className="field-label">
            Responder Department
            <select className="field" value={form.responder_type} onChange={(e) => setForm({ ...form, responder_type: e.target.value })}>
              <option>Sanitation Department</option>
              <option>Water Department</option>
              <option>Electrical Department</option>
              <option>Roads Department</option>
              <option>Fire</option>
              <option>Police</option>
              <option>Medical</option>
              <option>Disaster Response</option>
              <option>Women Support</option>
              <option>Child Support</option>
              <option>Elderly Assistance</option>
              <option>Community Volunteer</option>
            </select>
          </label>
        )}
        {form.role === "Responder" && (
          <label className="field-label">
            Availability
            <select className="field" value={form.availability_status} onChange={(e) => setForm({ ...form, availability_status: e.target.value })}>
              <option>Available</option>
              <option>Busy</option>
            </select>
          </label>
        )}
        <button className="primary-button">Register</button>
        <p className="text-center text-sm text-slate-600">Already registered? <Link className="link" to="/login">Sign in</Link></p>
      </form>
    </main>
  );
}
