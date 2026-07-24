# Sentinel AI

Sentinel AI is an AI-powered emergency response platform that enables citizens to report incidents in real time while automatically analyzing severity, classifying emergencies, recommending the appropriate responder department, and generating public safety advisories using Google Gemini AI.

- Frontend: React + Vite
- Backend: FastAPI
- Database: Supabase PostgreSQL Free
- AI: Google Gemini API
- Deployment: Vercel frontend, Render backend

## Features

- Citizen and responder authentication
- Citizen incident reporting with optional image/audio upload
- One-tap SOS emergency alerts
- Gemini-first incident analysis with local fallback only when Gemini is not configured or fails
- Department classification and responder routing
- SOS routing to every responder department
- Citizen dashboard showing all reported incidents
- Responder dashboard showing assigned/relevant incidents with status updates
- Clean PostgreSQL schema and reset scripts for a fresh cloud database

## AI Capabilities

- Incident severity prediction
- Emergency classification
- Department recommendation
- Public advisory generation
- Safety recommendations
- Confidence scoring
- Image-assisted incident analysis
- Local fallback if Gemini is unavailable

## Tech Stack

Frontend
- React
- Vite
- JavaScript
- Tailwind CSS

Backend
- FastAPI
- Python

Database
- Supabase PostgreSQL

Artificial Intelligence
- Google Gemini 2.5 Flash

Deployment
- Vercel
- Render

## System Architecture

```text
Citizen
    │
    ▼
React + Vite Frontend
    │
    ▼
FastAPI Backend
    │
    ├── Google Gemini 2.5 Flash
    ├── Supabase PostgreSQL
    └── Emergency Routing Engine
    │
    ▼
Responder Dashboard

## Backend Environment

Create `backend/.env`:

```env
APP_SECRET=replace-with-a-long-random-secret
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres?sslmode=require
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_ORIGIN=http://localhost:5173
```

For deployment, set `FRONTEND_ORIGIN` to your Vercel URL. Multiple origins are comma-separated:

```env
FRONTEND_ORIGIN=http://localhost:5173,https://your-app.vercel.app
```

## Frontend Environment

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

For Vercel:

```env
VITE_API_URL=https://your-render-backend.onrender.com
```

## Gemini API Setup

1. Open [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create an API key.
3. Add it to `backend/.env` as `GEMINI_API_KEY`.
4. Keep `GEMINI_MODEL=gemini-3.5-flash` unless you intentionally change models.

The backend loads `backend/.env` directly, so Gemini works whether you start FastAPI from the project root or from the backend folder. If the key is missing, left as the placeholder value, or Gemini throws an error, the app uses the local fallback so reporting still works.

## Supabase Database Setup

1. Create a free project at [Supabase](https://supabase.com).
2. Open **Project Settings > Database**.
3. Copy the PostgreSQL connection string.
4. Put it in `backend/.env` as `DATABASE_URL`.
5. Open Supabase SQL Editor.
6. Run all SQL from `backend/schema.sql`.
7. To start from a completely clean database, run `backend/reset_database.sql`.

You can also reset from PowerShell after configuring `DATABASE_URL`:

```powershell
cd backend
.\.venv\Scripts\python reset_database.py
```

This removes all app records from `users`, `incidents`, and `responder_assignments`.

## Run Locally

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Local URLs:

```text
Backend:  http://localhost:8000
Frontend: http://localhost:5173
```

## Incident Flow

1. Citizen submits a report.
2. Backend analyzes it with Gemini first.
3. Backend stores the incident in Supabase PostgreSQL.
4. Backend classifies the correct responder department.
5. Matching available responders receive assignments.
6. SOS reports are marked Critical and assigned to every available responder.
7. Dashboards fetch the latest data from the API; responder dashboard also polls for updates.

## Render Backend Deployment

1. Push the project to GitHub.
2. Open [Render](https://render.com).
3. Create **New Web Service**.
4. Connect your GitHub repository.
5. Set root directory to `backend`.
6. Build command: `pip install -r requirements.txt`
7. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
8. Add environment variables:

```env
APP_SECRET=replace-with-a-long-random-secret
DATABASE_URL=your_supabase_postgres_connection_string
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-3.5-flash
FRONTEND_ORIGIN=https://your-vercel-app.vercel.app
```

Deploy, then open `/health` on the Render URL to confirm the API is running.

## Vercel Frontend Deployment

1. Open [Vercel](https://vercel.com).
2. Import your GitHub repository.
3. Set root directory to `frontend`.
4. Build command: `npm run build`
5. Output directory: `dist`
6. Add environment variable:

```env
VITE_API_URL=https://your-render-backend.onrender.com
```

Deploy the frontend after the backend URL is live.

## Final Test Checklist

1. Run `backend/schema.sql` in Supabase.
2. Run `backend/reset_database.sql` once to clear old data.
3. Register one citizen.
4. Register responders for Sanitation, Water, Roads, Electrical, Fire, Medical, and Police.
5. Submit a normal citizen report and confirm only the matching department sees it.
6. Submit an SOS alert and confirm every responder sees it at the top.
7. Accept, update, and resolve an incident from a responder account.
8. Refresh both dashboards and confirm the data persists from Supabase.
