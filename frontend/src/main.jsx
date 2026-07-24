import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import App from "./App.jsx";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import CitizenDashboard from "./pages/CitizenDashboard.jsx";
import IncidentDetail from "./pages/IncidentDetail.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import ReportIncident from "./pages/ReportIncident.jsx";
import ResponderDashboard from "./pages/ResponderDashboard.jsx";
import "./styles.css";

function ProtectedRoute({ children, role }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="screen-center">Loading Sentinel AI...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) {
    return <Navigate to={user.role === "Responder" ? "/responder" : "/citizen"} replace />;
  }
  return children;
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<App />}>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/citizen"
              element={
                <ProtectedRoute role="Citizen">
                  <CitizenDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/report"
              element={
                <ProtectedRoute role="Citizen">
                  <ReportIncident />
                </ProtectedRoute>
              }
            />
            <Route
              path="/responder"
              element={
                <ProtectedRoute role="Responder">
                  <ResponderDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/incidents/:id"
              element={
                <ProtectedRoute>
                  <IncidentDetail />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
