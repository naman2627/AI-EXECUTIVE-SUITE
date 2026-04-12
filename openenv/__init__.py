from openenv.tasks.ceo import CEOTask
from openenv.tasks.cfo import CFOTask
from openenv.tasks.cto import CTOTask
from openenv.graders.ceo_grader import grade_ceo
from openenv.graders.cfo_grader import grade_cfo
from openenv.graders.cto_grader import grade_cto
from openenv.env import OpenEnv

# Task registry — maps task name to its class and grader function.
# The evaluation platform discovers tasks via this dict and checks that
# each entry has a callable grader that returns a float in (0, 1).
TASKS = {
    "ceo": {
        "task_class": CEOTask,
        "grader": grade_ceo,
    },
    "cfo": {
        "task_class": CFOTask,
        "grader": grade_cfo,
    },
    "cto": {
        "task_class": CTOTask,
        "grader": grade_cto,
    },
}


def get_tasks():
    """Return a list of instantiated task objects, each with a grader attached.

    Each object in the returned list has:
      - task_id  (str)       — unique task identifier (class attribute)
      - grader   (callable)  — function(state: dict) -> float strictly in (0, 1)
                               i.e. 0.0 and 1.0 are excluded (open interval)
      - grade()  (method)    — convenience wrapper on the task itself
    """
    instances = []
    for name, entry in TASKS.items():
        task = entry["task_class"]()
        task.grader = entry["grader"]
        instances.append(task)
    return instances


__all__ = [
    "OpenEnv",
    "TASKS",
    "get_tasks",
    "CEOTask",
    "CFOTask",
    "CTOTask",
    "grade_ceo",
    "grade_cfo",
    "grade_cto",
]
