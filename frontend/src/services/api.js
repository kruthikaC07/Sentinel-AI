export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

let authToken = localStorage.getItem("sentinel_token");

export function setToken(token) {
  authToken = token;
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  let body = options.body;

  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(body);
  }

  if (authToken) headers.Authorization = `Bearer ${authToken}`;

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
      body
    });
  } catch (err) {
    throw new Error(`Cannot reach Sentinel AI API at ${API_URL}. Make sure the FastAPI backend is running and VITE_API_URL points to it.`);
  }

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(data?.detail || "Request failed");
  }
  return data;
}
