import random
from openenv.models import Action, Observation
from openenv.graders.cfo_grader import grade_cfo

class CFOTask:
    def reset(self, inputs: dict = None):
        inputs = inputs or {}
        self.cash = float(inputs.get("cash", 5000.0))
        self.burn_rate = float(inputs.get("burn_rate", 500.0))
        self.expenses = float(inputs.get("expenses", 2000.0))
        self.revenue = float(inputs.get("revenue", 3000.0))
        self.step_count = 0

    def get_state(self) -> dict:
        return {
            "cash": round(self.cash, 2),
            "burn_rate": round(self.burn_rate, 2),
            "expenses": round(self.expenses, 2),
            "revenue": round(self.revenue, 2),
        }

    def grade(self, state: dict = None) -> float:
        return grade_cfo(state or self.get_state())

    def step(self, action: Action) -> Observation:
        self.step_count += 1

        if action.type == "cut_costs":
            self.expenses *= 0.85
            self.burn_rate *= 0.9
            base_reward = 3.0

        elif action.type == "increase_marketing":
            self.expenses *= 1.1
            self.revenue *= 1.15
            base_reward = 4.0

        elif action.type == "invest_growth":
            self.expenses *= 1.2
            self.revenue *= 1.25
            self.burn_rate *= 1.1
            base_reward = 5.0

        elif action.type == "hold":
            base_reward = 1.0

        else:
            base_reward = 0.0

        # Natural growth
        self.revenue *= 1.03
        profit = self.revenue - self.expenses

        # Real math: total cash increases/decreases exactly by profit
        self.cash = max(100.0, self.cash + profit)

        # Burn rate is either actual net loss, or base expenses
        self.burn_rate = max(100.0, self.expenses - self.revenue if profit < 0 else self.expenses * 0.5)

        runway = self.cash / max(self.burn_rate, 1)
        profit_margin = (self.revenue - self.expenses) / max(self.revenue, 1)
        reward = base_reward * 0.5 + max(0, profit_margin) * 30 + min(runway, 12) * 0.3

        done = self.step_count >= 10
        return Observation(
            state=self.get_state(),
            reward=round(reward, 2),
            done=done,
            info={"profit": round(profit, 2), "runway_months": round(runway, 1)}
        )
