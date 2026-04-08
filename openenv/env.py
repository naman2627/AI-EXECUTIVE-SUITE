from openenv.models import Action, Observation
from openenv.tasks.ceo import CEOTask
from openenv.tasks.cfo import CFOTask
from openenv.tasks.cto import CTOTask

class OpenEnv:
    def __init__(self, task: str):
        self.task_name = task
        if task == "ceo":
            self.task = CEOTask()
        elif task == "cfo":
            self.task = CFOTask()
        elif task == "cto":
            self.task = CTOTask()
        else:
            raise ValueError(f"Unknown task: {task}")

    def reset(self):
        self.task.reset()
        return self.task.get_state()

    def step(self, action: Action) -> Observation:
        return self.task.step(action)

    def state(self) -> dict:
        return self.task.get_state()