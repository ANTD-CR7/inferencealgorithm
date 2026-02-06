
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import experiment_utils as utils
from experiment_utils import get_all_networks

app = FastAPI(title="Bayesian Inference Lab", docs_url="/api/docs", redoc_url=None)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class InferenceRequest(BaseModel):
    network: str
    algorithm: str  # "ve" or "gibbs"
    query_var: str
    evidence: Dict[str, int]
    samples: Optional[int] = 10000

class NetworkInfo(BaseModel):
    name: str
    variables: List[str]
    nodes: List[str]
    edges: List[List[str]]
    cpt_sizes: Dict[str, int] = {}
    state_counts: Dict[str, int] = {}
    total_cpt_entries: int = 0

# --- API Endpoints ---

@app.get("/health")
async def health_check():
    """Health check endpoint for Render."""
    return {"status": "healthy"}


@app.get("/api/networks", response_model=List[NetworkInfo])
async def get_networks():
    """Returns available networks and their structure."""
    networks = get_all_networks()
    info_list = []
    for name, model in networks.items():
        cpt_sizes: Dict[str, int] = {}
        state_counts: Dict[str, int] = {}
        total_cpt_entries = 0

        for node in model.nodes():
            cpd = model.get_cpds(node)
            if cpd is None:
                continue
            try:
                size = int(cpd.values.size)
            except Exception:
                size = 0
            cpt_sizes[node] = size
            try:
                state_counts[node] = int(getattr(cpd, "variable_card", 0) or 0)
            except Exception:
                state_counts[node] = 0
            total_cpt_entries += size

        info_list.append(NetworkInfo(
            name=name,
            variables=list(model.nodes()),
            nodes=list(model.nodes()),
            edges=[list(edge) for edge in model.edges()],
            cpt_sizes=cpt_sizes,
            state_counts=state_counts,
            total_cpt_entries=total_cpt_entries
        ))
    return info_list

@app.post("/api/inference")
async def run_inference(req: InferenceRequest):
    """Runs inference on the specified network."""
    networks = get_all_networks()
    if req.network not in networks:
        raise HTTPException(status_code=404, detail="Network not found")
    
    model = networks[req.network]
    
    # Check if query_var exists
    if req.query_var not in model.nodes():
         raise HTTPException(status_code=400, detail=f"Query variable {req.query_var} not in network")

    # Result structure
    result = {
        "algorithm": req.algorithm,
        "probabilities": {},
        "time_ms": 0.0,
        "samples": 0
    }

    try:
        if req.algorithm == "ve":
            # Variable Elimination
            # We want full distribution P(Q | E)
            # The utils run_exact_inference returns scalar probability for a target state
            # Here we want the full distribution. We'll use pgmpy directly or modify utils.
            # Let's use pgmpy directly for full distribution to return both states.
            from pgmpy.inference import VariableElimination
            import time
            
            start = time.time()
            ve = VariableElimination(model)
            ve_res = ve.query([req.query_var], evidence=req.evidence, show_progress=False)
            duration = time.time() - start
            
            # Map values to 0 and 1
            result["probabilities"] = {
                "0": ve_res.values[0],
                "1": ve_res.values[1]
            }
            result["time_ms"] = duration * 1000

        elif req.algorithm == "gibbs":
            # Gibbs Sampling
            # Use utils but we need full distribution, utils currently returns scalar for target=1
            # We can use utils.run_gibbs_inference and derive 0 from 1, or just re-implement slightly
            # to be safe and return standard format.
            prob_1, duration = utils.run_gibbs_inference(
                model, req.query_var, req.evidence, req.samples, target_state=1
            )
            prob_0 = 1.0 - prob_1
            
            result["probabilities"] = {
                "0": prob_0,
                "1": prob_1
            }
            result["time_ms"] = duration * 1000
            result["samples"] = req.samples
            
        else:
             raise HTTPException(status_code=400, detail="Invalid algorithm")

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_index():
    return FileResponse("web_app/index.html")

# Mount web_app at root for .css and .js
if os.path.exists("web_app"):
    app.mount("/", StaticFiles(directory="web_app"), name="static")

# Mount results for PNGs
app.mount("/results", StaticFiles(directory="."), name="results")

if __name__ == "__main__":
    import uvicorn
    print(" Starting Bayesian Inference Lab Server...")
    print(" Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
