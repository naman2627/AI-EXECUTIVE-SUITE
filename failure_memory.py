# failure_memory.py

import json
import os

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)
MEMORY_FILE = os.path.join(MEMORY_DIR, "failure_memory.json")


def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"ceo": [], "cfo": [], "cto": []}


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def record_failure(task, state, action, issue):
    memory = load_memory()
    memory[task].append({
        "state": state,
        "action": action,
        "issue": issue
    })
    memory[task] = memory[task][-20:]  # Keep last 20 failures
    save_memory(memory)


def get_recent_failures(task):
    memory = load_memory()
    return memory.get(task, [])[-3:]  # Return last 3 failures
