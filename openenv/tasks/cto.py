import random
from openenv.models import Action, Observation

class CTOTask:
    def reset(self, inputs: dict = None):
        inputs = inputs or {}
        self.feature_backlog = 20
        self.step_count = 0

    def get_state(self) -> dict:
        return {
            "feature_backlog": self.feature_backlog
        }

    def step(self, action: Action) -> Observation:
        self.step_count += 1

        if action.type == "build_feature":
            self.feature_backlog = max(0, self.feature_backlog - 3)
            reward = 4.0

        elif action.type == "scale_infrastructure":
            reward = 3.0

        elif action.type == "ignore":
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