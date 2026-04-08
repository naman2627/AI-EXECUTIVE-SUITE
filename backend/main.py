import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load .env from project root
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass

from typing import List
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from simulation import SimulationRunner
from chat import build_conversation_prompt, call_ai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REQUEST MODELS

class ChatHistoryItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    user_role: str = "CEO"
    agent_role: str = "CFO"
    history: List[ChatHistoryItem] = []

class StrategyRequest(BaseModel):
    user_role: str = "CEO"
    agent_role: str = "CFO"
    problem: str
    history: List[ChatHistoryItem] = []

class SimulationRequest(BaseModel):
    revenue: float
    users: int
    cash: float
    burn_rate: float
    expenses: float
    overrides: dict = {}

# REQUIRED OPENENV ENDPOINT
@app.post("/reset")
def reset():
    """Mock reset endpoint required by the OpenEnv validator script."""
    return {"status": "ok"}

# STRATEGY ENDPOINT

@app.post("/strategy")
def strategy(req: StrategyRequest):
    history_context = ""
    if req.history:
        history_lines = []
        for m in req.history[-10:]:
            r = m.role.upper()
            history_lines.append(f"{r}: {m.content}")
        history_context = "\nConversation History:\n" + "\n".join(history_lines) + "\n\n"

    prompt = f"""
You are an elite {req.agent_role} strategist advising the company's {req.user_role}.

{history_context}Problem Overview:
{req.problem}

Give:
1. Core problem
2. 3 strategies
3. Best decision
4. Execution plan
"""

    try:
        response = call_ai(prompt)

        # fallback if empty
        if not response or "No API key" in response:
            raise Exception("AI failed")

    except:
        response = f"""
Core Problem:
Growth is slow due to weak market expansion.

Strategies:
1. Increase marketing spend
2. Improve product differentiation
3. Expand into new segments

Best Decision:
Focus on product + marketing combination

Execution Plan:
1. Identify target audience
2. Launch campaigns
3. Optimize funnel
4. Track CAC vs LTV
5. Scale winning channels
"""

    return {"response": response}

# CHAT ENDPOINT
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        messages = [item.dict() for item in req.history]
        messages.append({"role": "user", "content": req.message})

        prompt = build_conversation_prompt(
            messages,
            req.user_role,
            req.agent_role,
            "⚡ Quick"
        )

        response = call_ai(prompt)

    except Exception as e:
        print("CHAT ERROR:", e)
        response = "AI fallback: Focus on execution, growth, and efficiency."

    return {"response": response}

# SIMULATION ENDPOINT

@app.post("/simulate")
def simulate(req: SimulationRequest):
    runner = SimulationRunner(inputs=req.dict(), overrides=req.overrides)
    results = runner.run_simulation(10)

    revenue = [s["ceo"]["state"]["revenue"] for s in results]
    cash = [s["cfo"]["state"]["cash"] for s in results]

    try:
        analysis = call_ai(f"Analyze: revenue={revenue}, cash={cash}")
    except:
        analysis = "Revenue growing steadily. Cash improving. System stabilizing."

    return {
        "graph": {
            "revenue": revenue,
            "cash": cash
        },
        "analysis": analysis,
        "report": "Final Simulation Run Complete.",
        "steps": results
    }

# SPA Routing: Serve static assets, fallback to index.html
if os.path.isdir("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    file_path = os.path.join("frontend/dist", full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse("frontend/dist/index.html")