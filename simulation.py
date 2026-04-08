# simulation.py
import os
from typing import Dict, List
from openenv.env import OpenEnv
from openenv.models import Action
from openenv.graders import grade_ceo, grade_cfo, grade_cto
from failure_memory import record_failure, get_recent_failures

class SimulationRunner:
    def __init__(self, inputs: dict = None, overrides: dict = None):
        inputs = inputs or {}
        self.overrides = overrides or {}
        from openenv.tasks.ceo import CEOTask
        from openenv.tasks.cfo import CFOTask
        from openenv.tasks.cto import CTOTask

        self.ceo_task = CEOTask()
        self.cfo_task = CFOTask()
        self.cto_task = CTOTask()

        self.ceo_task.reset(inputs)
        self.cfo_task.reset(inputs)
        self.cto_task.reset(inputs)

    def run_simulation(self, steps: int = 10) -> List[Dict]:
        """Run simulation for specified number of steps."""
        results = []

        for step in range(steps):
            step_results = {}
            step_override = self.overrides.get(str(step), {})

            # ── CEO turn ──────────────────────────────────────────────────────
            ceo_state = self.ceo_task.get_state()
            if "ceo" in step_override:
                ceo_action = Action(type=step_override["ceo"])
                ceo_reason = "Manual override by Executive."
            elif ceo_state["revenue"] < 3000:
                ceo_action = Action(type="expand_market")
                ceo_reason = "Revenue below threshold, expanding market to drive growth."
            else:
                ceo_action = Action(type="launch_feature")
                ceo_reason = "Revenue healthy, launching a new feature to capture demand."
            ceo_obs = self.ceo_task.step(ceo_action)
            ceo_score = grade_ceo(self.ceo_task.get_state())

            if ceo_obs.reward < 0:
                record_failure("ceo", ceo_state, ceo_action.type, "Negative reward on CEO decision")

            step_results["ceo"] = {
                "action": ceo_action.type,
                "reason": ceo_reason,
                "reward": ceo_obs.reward,
                "score": ceo_score,
                "state": self.ceo_task.get_state().copy(),
            }

            # ── CFO turn ──────────────────────────────────────────────────────
            cfo_state = self.cfo_task.get_state()
            if "cfo" in step_override:
                cfo_action = Action(type=step_override["cfo"])
                cfo_reason = "Manual override by Executive."
            elif cfo_state["cash"] < 2000:
                cfo_action = Action(type="cut_costs")
                cfo_reason = "Cash is low, cutting costs to protect runway."
            else:
                cfo_action = Action(type="invest_growth")
                cfo_reason = "Cash is stable, investing in growth opportunities."
            cfo_obs = self.cfo_task.step(cfo_action)
            cfo_score = grade_cfo(self.cfo_task.get_state())

            new_cfo_state = self.cfo_task.get_state()
            if step > 0 and new_cfo_state["cash"] < cfo_state["cash"]:
                record_failure("cfo", cfo_state, cfo_action.type, "cash decreased")
            profit = new_cfo_state.get("revenue", 0) - new_cfo_state.get("expenses", 0)
            if profit < 0:
                record_failure("cfo", cfo_state, cfo_action.type, "negative profit")

            step_results["cfo"] = {
                "action": cfo_action.type,
                "reason": cfo_reason,
                "reward": cfo_obs.reward,
                "score": cfo_score,
                "state": new_cfo_state.copy(),
            }

            # ── CTO turn ──────────────────────────────────────────────────────
            cto_state = self.cto_task.get_state()
            if "cto" in step_override:
                cto_action = Action(type=step_override["cto"])
                cto_reason = "Manual override by Executive."
            elif cto_state.get("feature_backlog", 0) > 10:
                cto_action = Action(type="build_feature")
                cto_reason = "Feature backlog is high, building new features."
            else:
                cto_action = Action(type="scale_infrastructure")
                cto_reason = "Features are under control, scaling infrastructure."
            cto_obs = self.cto_task.step(cto_action)
            cto_score = grade_cto(self.cto_task.get_state())

            if cto_obs.reward < 0:
                record_failure("cto", cto_state, cto_action.type, "Negative reward on CTO decision")

            step_results["cto"] = {
                "action": cto_action.type,
                "reason": cto_reason,
                "reward": cto_obs.reward,
                "score": cto_score,
                "state": self.cto_task.get_state().copy(),
            }

            results.append(step_results)

        return results

    def get_final_scores(self, results: List[Dict]) -> Dict[str, float]:
        if not results:
            return {"ceo": 0.0, "cfo": 0.0, "cto": 0.0}
        final = results[-1]
        return {
            "ceo": final["ceo"]["score"],
            "cfo": final["cfo"]["score"],
            "cto": final["cto"]["score"],
        }

def run_quick_simulation() -> Dict:
    """Run a 5-step simulation for the sidebar quick action."""
    runner = SimulationRunner()
    results = runner.run_simulation(5)
    return runner.get_final_scores(results)

def run_simulation(decision_mode: str, inputs: Dict, manual_action_provider=None, steps: int = 10):
    env = OpenEnv()
    env.reset(inputs)
    
    results = []
    for step in range(steps):
        if decision_mode == "AI":
            actions = {}
            for role in ["ceo", "cfo", "cto"]:
                state = env.get_state(role)
                if role == "ceo":
                    if state["revenue"] < 3000:
                        action = Action(type="expand_market")
                        reason = "Revenue below threshold, expanding market."
                    else:
                        action = Action(type="launch_feature")
                        reason = "Revenue healthy, launching a new feature."
                elif role == "cfo":
                    if state["cash"] < 2000:
                        action = Action(type="cut_costs")
                        reason = "Cash is low, cutting costs to protect runway."
                    else:
                        action = Action(type="invest_growth")
                        reason = "Cash is stable, investing in growth."
                else:
                    if state.get("feature_backlog", 0) > 10:
                        action = Action(type="build_feature")
                        reason = "Feature backlog is high, prioritizing new features."
                    else:
                        action = Action(type="scale_infrastructure")
                        reason = "Features are under control, scaling infrastructure."
                actions[role] = action
        else:
            actions = manual_action_provider()
            
        obs = env.step(actions)
        results.append({
            "step": step + 1,
            "ceo": {"action": actions["ceo"].type, "reason": getattr(actions["ceo"], 'reason', '')},
            "cfo": {"action": actions["cfo"].type, "reason": getattr(actions["cfo"], 'reason', '')},
            "cto": {"action": actions["cto"].type, "reason": getattr(actions["cto"], 'reason', '')},
        })
        
        if obs.ceo.reward < 0:
            record_failure("ceo", env.get_state("ceo"), actions["ceo"].type, "Negative reward")
        if obs.cfo.reward < 0:
            record_failure("cfo", env.get_state("cfo"), actions["cfo"].type, "Negative reward")
        if obs.cto.reward < 0:
            record_failure("cto", env.get_state("cto"), actions["cto"].type, "Negative reward")
    
    return obs