#!/usr/bin/env python3
"""
Validates that the evaluator can discover >= 3 tasks with graders.

This script mimics the evaluation platform's Phase 2 Task Validation step:
  1. Import the openenv package.
  2. Read the TASKS registry (dict mapping task_id -> {task_class, grader}).
  3. Instantiate each task, reset it, and call the grader.
  4. Assert that at least 3 tasks have callable graders returning a float
     strictly between 0 and 1 — i.e. in the open interval (0, 1), so
     boundary values 0.0 and 1.0 are intentionally excluded.

Run with:
    python test_task_discovery.py
"""

import sys


def main() -> int:
    print("=" * 60)
    print("Phase 2 Task Validation — discovery check")
    print("=" * 60)

    # Step 1: import package
    try:
        import openenv
        print("[OK] import openenv")
    except Exception as exc:
        print(f"[FAIL] import openenv: {exc}")
        return 1

    # Step 2: TASKS registry must exist and be non-empty
    tasks_registry = getattr(openenv, "TASKS", None)
    if not tasks_registry:
        print("[FAIL] openenv.TASKS is missing or empty")
        return 1
    print(f"[OK] openenv.TASKS found with {len(tasks_registry)} entries: {list(tasks_registry.keys())}")

    # Step 3: discover tasks with valid graders
    tasks_with_graders = []
    for task_id, entry in tasks_registry.items():
        task_class = entry.get("task_class")
        grader = entry.get("grader")

        if task_class is None:
            print(f"[FAIL] {task_id}: missing task_class")
            continue
        if not callable(grader):
            print(f"[FAIL] {task_id}: grader is not callable")
            continue

        try:
            task = task_class()
            task.reset()
            state = task.get_state()
        except Exception as exc:
            print(f"[FAIL] {task_id}: task instantiation/reset error: {exc}")
            continue

        try:
            score = grader(state)
        except Exception as exc:
            print(f"[FAIL] {task_id}: grader raised an error: {exc}")
            continue

        if not isinstance(score, float):
            print(f"[FAIL] {task_id}: grader returned {type(score).__name__}, expected float")
            continue
        if not (0.0 < score < 1.0):
            print(f"[FAIL] {task_id}: grader score {score} is not strictly in (0, 1)")
            continue

        print(f"[OK]   {task_id}: grader={grader.__name__}  score={score}")
        tasks_with_graders.append(task_id)

    print()
    print(f"Tasks with valid graders: {tasks_with_graders}")
    print(f"Count: {len(tasks_with_graders)}")

    if len(tasks_with_graders) < 3:
        print("\n[FAIL] Not enough tasks with graders.")
        print("       Your submission must include at least 3 tasks with graders.")
        return 1

    print("\n[PASS] Task Validation — at least 3 tasks with graders found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
