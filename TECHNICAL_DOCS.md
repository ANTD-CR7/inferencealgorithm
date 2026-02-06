# Technical Documentation

## 1. Project Overview
The Bayesian Inference Lab is a client?server system that enables interactive exploration of Bayesian networks. A static frontend provides visualization and user controls, while a FastAPI backend performs inference (Variable Elimination and Gibbs Sampling) and returns results.

---

## 2. Architecture Summary
**Frontend (static web app)**
- Directory: `web_app/`
- Libraries: vis-network (graph), Plotly (charts), GSAP (animations), Spline Viewer (3D)
- Responsibilities: UI rendering, evidence selection, algorithm selection, results display

**Backend (FastAPI)**
- File: `server.py`
- Endpoints:
  - `GET /api/networks`
  - `POST /api/inference`
- Responsibilities: load networks, run inference, return results + latency

**Data/Models**
- Bayesian networks: Synthetic, Alarm, Student
- Utilities: `experiment_utils.py`

---

## 3. API Reference

### `GET /api/networks`
**Description:** returns available networks and metadata.

**Response (sample):**
```json
[
  {
    "name": "Alarm (4 vars)",
    "variables": ["Burglary","Alarm","Earthquake","PhoneCall"],
    "nodes": ["Burglary","Alarm","Earthquake","PhoneCall"],
    "edges": [["Burglary","Alarm"],["Earthquake","Alarm"],["Alarm","PhoneCall"]],
    "cpt_sizes": {"Burglary":2,"Alarm":8,"Earthquake":2,"PhoneCall":4},
    "state_counts": {"Burglary":2,"Alarm":2,"Earthquake":2,"PhoneCall":2},
    "total_cpt_entries": 16
  }
]
```

### `POST /api/inference`
**Description:** runs inference on a chosen network.

**Body:**
```json
{
  "network": "Alarm (4 vars)",
  "algorithm": "ve",
  "query_var": "Alarm",
  "evidence": {"Burglary": 1},
  "samples": 10000
}
```

**Response:**
```json
{
  "algorithm": "ve",
  "probabilities": {"0": 0.12, "1": 0.88},
  "time_ms": 4.2,
  "samples": 0
}
```

---

## 4. Frontend Behavior

### Evidence Selection
- Click node cycles: **TRUE ? FALSE ? clear**
- Query node cannot be evidence; it auto?switches to another variable.

### Comparison Mode
- Compare (VE vs Gibbs) unlocks after first inference run.

### Performance
- Spline loads lazily when visible.
- Mobile rendering is optimized via styling and spacing.

---

## 5. Local Development

### Backend (FastAPI)
```bash
pip install -r backend/requirements.txt
python server.py
```

### Frontend
Open `web_app/index.html` in a browser, or serve via a static server.

---

## 6. Deployment

### Frontend
- Vercel (static hosting)

### Backend
- Render (FastAPI service)
- Set the API base in `web_app/index.html`:
```html
<script>
  window.API_BASE = "https://your-backend.onrender.com/api";
</script>
```

---

## 7. Configuration Notes
- `API_BASE` defaults to `/api`, but can be overridden using `window.API_BASE`.
- Evidence is stored locally for session persistence.
