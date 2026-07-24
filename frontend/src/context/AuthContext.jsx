import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, setToken } from "../services/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("sentinel_user") || "null"));
  const [token, setStoredToken] = useState(() => localStorage.getItem("sentinel_token"));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setToken(token);
  }, [token]);

  async function login(email, password) {
    const data = await api("/auth/login", { method: "POST", body: { email, password } });
    localStorage.setItem("sentinel_token", data.token);
    localStorage.setItem("sentinel_user", JSON.stringify(data.user));
    setStoredToken(data.token);
    setUser(data.user);
    return data.user;
  }

  async function register(payload) {
    const data = await api("/auth/register", { method: "POST", body: payload });
    localStorage.setItem("sentinel_token", data.token);
    localStorage.setItem("sentinel_user", JSON.stringify(data.user));
    setStoredToken(data.token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    localStorage.removeItem("sentinel_token");
    localStorage.removeItem("sentinel_user");
    setStoredToken(null);
    setUser(null);
  }

  const value = useMemo(() => ({ user, token, loading, login, register, logout }), [user, token, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
