# inferencealgorithm

## Live Demo
- https://inferencealgorithm.vercel.app/

## User-Centered Design (UCD)
This project is explicitly designed around **User-Centered Design (UCD)** principles, prioritizing clarity, accessibility, and interaction over raw technical complexity. The goal is not just to compute Bayesian inference, but to make it **understandable and usable** for real users.

**How UCD is emphasized:**
- Direct interaction over forms (click nodes to set evidence)
- Immediate feedback after inference runs
- Guided discovery with hints and legends
- Error prevention via query-node highlighting
- Progressive complexity (comparison is optional)
- Responsive design for mobile usability

## Frontend (Vercel)
- The static UI lives in `web_app/`.
- Vercel is configured via `vercel.json` at the repo root.
- Deploy by importing the GitHub repo in Vercel. It will auto-use `web_app` as the root.

### One-click Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ANTD-CR7/inferencealgorithm)

## Backend (later)
- Backend artifacts are in `backend/`.
- `backend/Dockerfile` runs `server.py` on port 8000.
- `backend/requirements.txt` contains the API dependencies.
- `backend/compose.yaml` can be used for local dev.

### Local backend (optional)
```powershell
cd backend
# From repo root
# Build and run with Docker:
docker compose up --build
```

## Notes
- If you add API endpoints, consider deploying the backend separately (Render/Railway/Fly) and set `API_BASE` in `web_app/app.js` to the deployed URL.
