from openenv.env import OpenEnv
from openenv.graders.ceo_grader import grade_ceo
from openenv.graders.cfo_grader import grade_cfo
from openenv.graders.cto_grader import grade_cto
from openenv.models import Action
from ai_decisions import ai_choose_action


def run_baseline():
    tasks = ["ceo", "cfo", "cto"]
    graders = {"ceo": grade_ceo, "cfo": grade_cfo, "cto": grade_cto}

    for task in tasks:
        env = OpenEnv(task)
        env.reset()
        print(f"Running {task.upper()} environment...")

        # Run for 10 steps with simple rule-based decisions
        for step in range(10):
            state = env.state()
            action, reason = ai_choose_action(task, state)
            obs = env.step(action)
            print(f"Step {step+1}:")
            print(f"  Action: {action.type}")
            print(f"  Reason: {reason}")
            print(f"  Reward: {obs.reward:.2f}")

        final_state = env.state()
        score = graders[task](final_state)
        print(f"Final score for {task.upper()}: {score:.2f}\n")


if __name__ == "__main__":
    run_baseline()