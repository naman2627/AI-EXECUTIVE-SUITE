# agents.py
from abc import ABC, abstractmethod
from typing import Dict, List
from ai_decisions import get_ai_decision
from failure_memory import get_recent_failures
import os

class ExecutiveAgent(ABC):
    def __init__(self, role: str):
        self.role = role

    @abstractmethod
    def decide(self, state: Dict, failures: List[Dict]) -> str:
        pass

class CEODecisionAgent(ExecutiveAgent):
    def __init__(self):
        super().__init__("ceo")

    def decide(self, state: Dict, failures: List[Dict]) -> str:
        return get_ai_decision(self.role, state, failures)

class CFODecisionAgent(ExecutiveAgent):
    def __init__(self):
        super().__init__("cfo")

    def decide(self, state: Dict, failures: List[Dict]) -> str:
        return get_ai_decision(self.role, state, failures)

class CTODecisionAgent(ExecutiveAgent):
    def __init__(self):
        super().__init__("cto")

    def decide(self, state: Dict, failures: List[Dict]) -> str:
        return get_ai_decision(self.role, state, failures)

class AgentCoordinator:
    def __init__(self):
        self.agents = {
            "ceo": CEODecisionAgent(),
            "cfo": CFODecisionAgent(),
            "cto": CTODecisionAgent()
        }

    def get_decision(self, role: str, state: Dict) -> str:
        failures = get_recent_failures(role)
        agent = self.agents.get(role.lower())
        if agent:
            return agent.decide(state, failures)
        return "hold"