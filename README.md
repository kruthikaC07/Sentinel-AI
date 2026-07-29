# Sentinel AI

<p align="center">
 AI-powered Emergency Decision Intelligence Platform
</p>

## ➡️Overview
Sentinel AI is an AI-powered emergency response platform that enables citizens to report incidents in real time while automatically analyzes incident severity, classifies emergencies, recommends the appropriate responder department, and generates public safety advisories using Google Gemini AI.

- Frontend: React + Vite
- Backend: FastAPI
- Database: Neon PostgreSQL Free
- AI: Google Gemini API
- Deployment: Vercel frontend, Render backend

## ➡️Features

- Citizen and responder authentication
- Citizen incident reporting with optional image/audio upload
- One-tap SOS emergency alerts
- AI-powered incident analysis with automatic local fallback when Gemini is unavailable.
- Department classification and responder routing
- SOS routing to every responder department
- Citizen dashboard showing all reported incidents
- AI-generated public safety advisories after incident reporting
- Responder dashboard showing assigned/relevant incidents with status updates
- Clean PostgreSQL schema and reset scripts for a fresh cloud database

## ➡️Screenshots

### 🔗Registration
<img width="1862" height="910" alt="sign up" src="https://github.com/user-attachments/assets/bbd440b7-b8ed-44d6-b382-7da511fefbcb" />

### 🔗Citizen Dashboard
<img width="1867" height="907" alt="citizen_dashboard_screenshot" src="https://github.com/user-attachments/assets/b0f8ca94-21af-49d3-af74-cfd2642de01c" />
<img width="1820" height="907" alt="citizen_dashboard_screenshot_2" src="https://github.com/user-attachments/assets/cd4c19d5-48d5-481e-b792-2b999faca522" />

### 🔗Incident Reporting
<img width="1860" height="917" alt="submitting" src="https://github.com/user-attachments/assets/69c1425d-d05b-4837-839f-73fca42de891" />

### 🔗AI Incident Analysis
<img width="1857" height="887" alt="report_screenshot" src="https://github.com/user-attachments/assets/c15f0b65-3af0-4b26-8f19-00b154de8cfb" />
<img width="1851" height="895" alt="report_screenshot_2" src="https://github.com/user-attachments/assets/42eafc8d-06ec-46be-bf21-46db0c072e69" />
<img width="1847" height="897" alt="report_screenshot_3" src="https://github.com/user-attachments/assets/39528525-017f-4fac-ae7b-cece0523266c" />
<img width="1802" height="886" alt="report_screenshot_4" src="https://github.com/user-attachments/assets/438ce7ae-68a3-4a8f-ae88-8e1860a115c7" />
<img width="1852" height="871" alt="report_screenshot_5" src="https://github.com/user-attachments/assets/2e4059df-7854-458e-b176-2053bc19b8bd" />

### 🔗Responder Dashboard
<img width="1861" height="897" alt="responder_dashboard_screenshot" src="https://github.com/user-attachments/assets/1ce40493-ce40-4316-9e8b-a31c8148e60f" />




## ➡️AI Capabilities

- Incident severity prediction
- Emergency classification
- Department recommendation
- Public advisory generation
- Safety recommendations
- Confidence scoring
- Image-assisted incident analysis
- Local fallback if Gemini is unavailable

## ➡️Tech Stack

### Frontend
- React
- Vite
- JavaScript
- Tailwind CSS

### Backend
- FastAPI
- Python

### Database
- Neon PostgreSQL

### Artificial Intelligence
- Google Gemini 2.5 Flash

### Deployment
- Vercel
- Render

## ➡️System Architecture

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
    ├── Neon PostgreSQL
    └── Emergency Routing Engine
    │
    ▼
Responder Dashboard
```

## Backend Environment

Create `backend/.env`:

```env
APP_SECRET=replace-with-a-long-random-secret
DATABASE_URL=postgresql://username:password@your-neon-host.neon.tech/neondb?sslmode=require
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

## ➡️Gemini API Setup

1. Open [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create an API key.
3. Add it to `backend/.env` as `GEMINI_API_KEY`.
4. Keep `GEMINI_MODEL=gemini-2.5-flash` unless you intentionally change models.

The backend loads `backend/.env` directly, so Gemini works whether you start FastAPI from the project root or from the backend folder. If the key is missing, left as the placeholder value, or Gemini throws an error, the app uses the local fallback so reporting still works.

## ➡️ Neon PostgreSQL Database Setup

1. Create a free project at **Neon** (https://neon.com).
2. Create a new PostgreSQL database.
3. Open your project dashboard and navigate to **Connection Details**.
4. Copy the PostgreSQL connection string.
5. Add it to `backend/.env` as `DATABASE_URL`.
6. Run all SQL from `backend/schema.sql` to create the required tables.
7. To start with a clean database, run `backend/reset_database.sql`.

You can also reset the database from PowerShell after configuring `DATABASE_URL`:

```powershell
cd backend
.\.venv\Scripts\python reset_database.py
```

This removes all application data from the `users`, `incidents`, and `responder_assignments` tables while keeping the database schema intact.


## ➡️Run Locally

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

## ➡️Incident Flow

1. Citizen submits a report.
2. Backend analyzes it with Gemini first.
3. Backend stores the incident in Neon PostgreSQL.
4. Backend classifies the correct responder department.
5. Matching available responders receive assignments.
6. SOS reports are marked Critical and assigned to every available responder.
7. Dashboards fetch the latest data from the API; responder dashboard also polls for updates.

## 🚀 Deployment Guide

## ➡️Backend Deployment(Render)

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
DATABASE_URL=your_neon_postgres_connection_string
GEMINI_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_ORIGIN=https://your-vercel-app.vercel.app
```

Deploy, then open `/health` on the Render URL to confirm the API is running.

## ➡️Frontend Deployment (Vercel)

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

## ➡️Final Test Checklist

1. Run `backend/schema.sql` in Neon.
2. Run `backend/reset_database.sql` once to clear old data.
3. Register one citizen.
4. Register responders for Sanitation, Water, Roads, Electrical, Fire, Medical, and Police.
5. Submit a normal citizen report and confirm only the matching department sees it.
6. Submit an SOS alert and confirm every responder sees it at the top.
7. Accept, update, and resolve an incident from a responder account.
8. Refresh both dashboards and confirm the data persists from Neon.

## ➡️Team

- [Kruthika C](https://github.com/kruthikaC07) 
- [Rakshitha R S](https://github.com/rakshithaagowda) 
