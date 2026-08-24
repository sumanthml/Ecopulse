# EcoPulse — Real-Time Environmental Pollution Monitoring and Analysis System

EcoPulse is a full-stack real-time environmental monitoring platform built with FastAPI, React, Supabase PostgreSQL, and Groq AI intelligence.

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy (Async), Uvicorn, Pandas, NumPy, Scikit-learn
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Recharts, React Leaflet, Lucide React
- **Database / Realtime**: Supabase PostgreSQL & Supabase Realtime
- **AI Intelligence**: Groq API (`llama-3.3-70b-versatile`)
- **Maps**: Leaflet + OpenStreetMap

---

## Monorepo Directory Structure

```text
ecopulse/
├── backend/            # FastAPI Python server & ML/AI pipeline
├── database/           # PostgreSQL Schema (schema.sql) & Seed Data (seed.sql)
├── frontend/           # React TypeScript Vite web app
└── docker-compose.yml
```

---

## Setup & Running Locally

### 1. Database Setup (Supabase)

1. Create a free project on [Supabase](https://supabase.com).
2. Go to the **SQL Editor** in your Supabase dashboard.
3. Paste and run the contents of [`database/schema.sql`](database/schema.sql) to set up tables, indexes, and real-time publications.
4. (Optional) Paste and run [`database/seed.sql`](database/seed.sql) to populate realistic historical sensor data for Indian cities (Chennai, Hyderabad, Bengaluru, Delhi, Mumbai).

---

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
```

Update your `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql+asyncpg://postgres:password@db.your-project.supabase.co:5432/postgres
GROQ_API_KEY=gsk_your_groq_api_key
DEMO_MODE=true
DATA_PROVIDER=simulator
```

Run the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

FastAPI Interactive Swagger Docs: `http://localhost:8000/docs`

---

### 3. Frontend Setup

```bash
cd frontend
npm install

# Create .env from template
cp .env.example .env
```

Update your `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

Run the development server:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Key Features

1. **Server-Calculated US EPA AQI**: Full breakpoint interpolation formula executed entirely server-side.
2. **Realistic Diurnal Simulator**: Time-series simulator modeling rush hour peaks, correlations (PM2.5/PM10, NO2/CO), and Gaussian noise.
3. **Groq AI Environmental Intelligence**: Generates daily reports, anomaly explanations, and recommendations using compact analytical summaries.
4. **Scikit-learn Forecasting**: RandomForest & GradientBoosting models for 1h, 3h, 6h PM2.5 forecasts.
5. **Isolation Forest Anomaly Detection**: Statistical anomaly detection for identifying sudden pollution spikes.
6. **Supabase Realtime Feed**: Webhooks and real-time subscriptions driving chart, gauge, map, and table updates without manual refreshes.
