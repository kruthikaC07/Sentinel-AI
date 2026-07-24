import { Outlet, Link, useNavigate } from "react-router-dom";
import { LayoutDashboard, LogOut, Moon, ShieldCheck, Siren, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "./context/AuthContext.jsx";
import { api } from "./services/api.js";
import { getReadableLocation } from "./utils/location.js";

export default function App() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem("sentinel_theme") !== "light");
  const [sosLoading, setSosLoading] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("sentinel_theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  function handleLogout() {
    logout();
    navigate("/login");
  }

  async function submitSOS() {
    if (!user || user.role !== "Citizen" || sosLoading) return;
    setSosLoading(true);
    try {
      const location = await getReadableLocation();
      if (!location) return;
      const incident = await api("/incidents/sos", {
        method: "POST",
        body: {
          location: location.address,
          latitude: location.latitude,
          longitude: location.longitude,
          description: "SOS emergency alert submitted by citizen."
        }
      });
      navigate(`/incidents/${incident.id}`);
    } catch (error) {
      window.alert(error.message || "Unable to submit SOS alert.");
    } finally {
      setSosLoading(false);
    }
  }

  return (
    <div className="app-shell min-h-screen text-slate-900">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <Link to={user?.role === "Responder" ? "/responder" : "/citizen"} className="flex items-center gap-3">
            <span className="brand-mark grid h-10 w-10 place-items-center rounded-lg bg-navy-900 text-white">
              <ShieldCheck size={22} />
            </span>
            <div>
              <p className="text-lg font-bold leading-tight text-navy-900">Sentinel AI</p>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Emergency Intelligence</p>
            </div>
          </Link>
          {user && (
            <div className="flex items-center gap-3">
              <Link className="nav-pill" to={user.role === "Responder" ? "/responder" : "/citizen"}>
                <LayoutDashboard size={16} />
                Dashboard
              </Link>
              {user.role === "Citizen" && (
                <button className="sos-button" onClick={submitSOS} disabled={sosLoading}>
                  <Siren size={17} />
                  {sosLoading ? "Sending" : "SOS"}
                </button>
              )}
              <div className="hidden text-right sm:block">
                <p className="text-sm font-semibold">{user.name}</p>
                <p className="text-xs text-slate-500">{user.role}{user.responder_type ? ` / ${user.responder_type}` : ""}</p>
              </div>
              <button className="icon-button" onClick={() => setDarkMode((value) => !value)} aria-label="Toggle dark mode" title="Toggle dark mode">
                {darkMode ? <Sun size={18} /> : <Moon size={18} />}
              </button>
              <button className="icon-button" onClick={handleLogout} aria-label="Log out" title="Log out">
                <LogOut size={18} />
                <span className="sr-only">Sign Out</span>
              </button>
              <button className="signout-button" onClick={handleLogout}>
                <LogOut size={16} />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </header>
      <Outlet />
    </div>
  );
}
