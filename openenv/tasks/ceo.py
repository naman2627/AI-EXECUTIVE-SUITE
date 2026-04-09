import random
from openenv.models import Action, Observation
from openenv.graders.ceo_grader import grade_ceo

class CEOTask:
    def reset(self, inputs: dict = None):
        inputs = inputs or {}
        self.revenue = float(inputs.get("revenue", 2000.0))
        self.users = int(inputs.get("users", 100))
        self.market_growth = 0.05
        self.competitor_pressure = 0.3
        self.step_count = 0

    def get_state(self) -> dict:
        return {
            "revenue": round(self.revenue, 2),
            "users": self.users,
            "market_growth": round(self.market_growth, 3),
            "competitor_pressure": round(self.competitor_pressure, 3),
        }

    def grade(self, state: dict = None) -> float:
        return grade_ceo(state or self.get_state())

    def step(self, action: Action) -> Observation:
        self.step_count += 1

        if action.type == "expand_market":
            growth = random.uniform(0.08, 0.15)
            self.revenue *= (1 + growth)
            self.users = int(self.users * (1 + growth * 0.8))
            self.market_growth = min(0.3, self.market_growth + 0.02)
            self.competitor_pressure = min(1.0, self.competitor_pressure + 0.05)
            reward = growth * 10

        elif action.type == "reduce_costs":
            self.revenue *= 0.97
            self.market_growth = max(0, self.market_growth - 0.01)
            reward = 2.0

        elif action.type == "launch_feature":
            user_growth = random.uniform(0.05, 0.20)
            self.users = int(self.users * (1 + user_growth))
            self.revenue *= (1 + user_growth * 0.5)
            reward = user_growth * 8

        elif action.type == "do_nothing":
            self.revenue *= (1 + self.market_growth * 0.3)
            reward = 0.5

        else:
            reward = 0.0

        # Natural market forces
        self.revenue *= (1 + self.market_growth * 0.02)

        done = self.step_count >= 10
        return Observation(
            state=self.get_state(),
            reward=round(reward, 2),
            done=done,
            info={"step": self.step_count}
        )
