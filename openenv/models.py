from pydantic import BaseModel
from typing import Dict, Any

class Action(BaseModel):
    type: str

class Observation(BaseModel):
    state: Dict[str, Any]
    reward: float
    done: bool
    info: Dict[str, Any] = {}