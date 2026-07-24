import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      const user = await login(form.email, form.password);
      navigate(user.role === "Responder" ? "/responder" : "/citizen");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="screen-center px-4">
      <form onSubmit={submit} className="auth-panel">
        <div>
          <p className="text-sm font-bold uppercase tracking-wide text-red-600">Command access</p>
          <h1 className="mt-2 text-3xl font-bold text-navy-900">Sign in to Sentinel AI</h1>
        </div>
        {error && <p className="alert">{error}</p>}
        <label className="field-label">Email<input className="field" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></label>
        <label className="field-label">Password<input className="field" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required /></label>
        <button className="primary-button">Login</button>
        <p className="text-center text-sm text-slate-600">New here? <Link className="link" to="/register">Create an account</Link></p>
      </form>
    </main>
  );
}
