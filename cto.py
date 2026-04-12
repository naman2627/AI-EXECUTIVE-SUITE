import random
from openenv.models import Action, Observation
from openenv.graders.cto_grader import grade_cto

class CTOTask:
    def __init__(self):
        self.reset()

    def reset(self, inputs: dict = None):
        inputs = inputs or {}
        self.feature_backlog = 20
        self.infra_score = 0.5
        self.step_count = 0

    def get_state(self) -> dict:
        return {
            "feature_backlog": self.feature_backlog,
            "infra_score": round(self.infra_score, 3),
        }

    def grade(self, state: dict = None) -> float:
        return grade_cto(state or self.get_state())

    def step(self, action: Action) -> Observation:
        self.step_count += 1

        if action.type == "fix_bugs":
            self.feature_backlog = max(1, self.feature_backlog - 2)
            self.infra_score = min(0.98, self.infra_score + 0.05)
            reward = 3.0

        elif action.type == "build_feature":
            self.feature_backlog = max(1, self.feature_backlog - 3)
            self.infra_score = min(0.98, self.infra_score + 0.03)
            reward = 4.0

        elif action.type == "scale_infrastructure":
            self.infra_score = min(0.98, self.infra_score + 0.08)
            reward = 3.0

        elif action.type == "ignore":
            self.feature_backlog = min(49, self.feature_backlog + 2)
            self.infra_score = max(0.02, self.infra_score - 0.05)
            reward = -1.0

        else:
            reward = 0.0

        done = self.step_count >= 10
        return Observation(
            state=self.get_state(),
            reward=round(reward, 2),
            done=done,
            info={"step": self.step_count}
        )