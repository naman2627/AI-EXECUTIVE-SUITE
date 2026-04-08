import asyncio
import os
import textwrap
from typing import List, Optional

from openai import OpenAI

from openenv.env import OpenEnv
from openenv.models import Action

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
TASK_NAME = os.getenv("MY_ENV_TASK", "ceo")
BENCHMARK = os.getenv("MY_ENV_BENCHMARK", "ai-executive-suite")
MAX_STEPS = 10
TEMPERATURE = 0.7
MAX_TOKENS = 150
SUCCESS_SCORE_THRESHOLD = 0.5  # normalized score in [0, 1]

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an AI Executive operating in a simulated startup environment.
    You must return a valid decision type exactly as code without quotes.
    For CEO: expand_market, reduce_costs, launch_feature, do_nothing
    For CFO: cut_costs, increase_marketing, invest_growth, hold
    For CTO: fix_bugs, build_feature, scale_infrastructure, ignore
    
    Choose the best action given the current context to maximize your score.
    Reply with exactly one action string - no quotes, no prefixes, just the action text.
    """
).strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def build_user_prompt(step: int, last_state: dict, last_reward: float, history: List[str]) -> str:
    history_block = "\n".join(history[-4:]) if history else "None"
    return textwrap.dedent(
        f"""
        Step: {step}
        Last state: {last_state}
        Last reward: {last_reward:.2f}
        Previous steps:
        {history_block}
        Send your next action text.
        """
    ).strip()


def get_model_message(client: OpenAI, step: int, last_state: dict, last_reward: float, history: List[str]) -> str:
    user_prompt = build_user_prompt(step, last_state, last_reward, history)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        # Ensure fallback validity
        safe_actions = ["do_nothing", "hold", "ignore", "expand_market", "reduce_costs", "launch_feature", "cut_costs", "increase_marketing", "invest_growth", "fix_bugs", "build_feature", "scale_infrastructure"]
        for act in safe_actions:
            if act in text:
                return act
        return "do_nothing"
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return "do_nothing"


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # Initialize environment synchronously (since OpenEnv matches our implementation)
    env = OpenEnv(task=TASK_NAME)

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        # Reset creates initial state
        last_state = env.reset()
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            
            message = get_model_message(client, step, last_state, last_reward, history)

            obs = env.step(Action(type=message))

            reward = obs.reward or 0.0
            done = obs.done
            error = None

            rewards.append(reward)
            steps_taken = step
            last_state = obs.state
            last_reward = reward

            log_step(step=step, action=message, reward=reward, done=done, error=error)

            history.append(f"Step {step}: {message!r} -> reward {reward:+.2f}")

            if done:
                break
        
        # Pull final grader score from state / task logic
        # In our implementation, we calculate grader at the end of sim or rely on accumulated rewards
        # We'll calculate score via our grader (available in env.task internally or run separately)
        # Mocking score behavior as total accumulated step rewards normalized to [0,1]
        score = sum(rewards) / (MAX_STEPS * 1.0)
        score = min(max(score, 0.0), 1.0)  # clamp to [0, 1]
        
        # We can also call the grader directly if available
        if hasattr(env.task, 'grade'):
            score = env.task.grade(env.task.get_state())
        
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        try:
            # We don't have an async close on our env object
            if hasattr(env, 'close'):
                env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}", flush=True)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
