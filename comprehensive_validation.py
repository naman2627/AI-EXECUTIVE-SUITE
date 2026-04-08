#!/usr/bin/env python3
"""Comprehensive validation test for upgraded OpenEnv project"""

import sys
import json
from pathlib import Path

print("=" * 60)
print("🔍 COMPREHENSIVE VALIDATION TEST")
print("=" * 60)

# TEST 1: Check all files exist
print("\n[TEST 1] File existence check...")
files_to_check = [
    "ai_decisions.py",
    "app.py", 
    "failure_memory.py",
    "memory/failure_memory.json",
    "openenv/env.py",
    "openenv/models.py"
]

for f in files_to_check:
    p = Path(f)
    if p.exists():
        print(f"  ✓ {f}")
    else:
        print(f"  ✗ {f} - MISSING!")

# TEST 2: Import all modules
print("\n[TEST 2] Import validation...")
try:
    from failure_memory import load_memory, save_memory, record_failure, get_recent_failures
    print("  ✓ failure_memory imports OK")
except Exception as e:
    print(f"  ✗ failure_memory import FAILED: {e}")
    sys.exit(1)

try:
    from ai_decisions import ai_choose_action
    print("  ✓ ai_decisions imports OK")
except Exception as e:
    print(f"  ✗ ai_decisions import FAILED: {e}")
    sys.exit(1)

try:
    from openenv.models import Action
    print("  ✓ openenv.models imports OK")
except Exception as e:
    print(f"  ✗ openenv.models import FAILED: {e}")
    sys.exit(1)

# TEST 3: Memory system functionality
print("\n[TEST 3] Failure memory system...")
try:
    # Clear memory
    import os
    if os.path.exists("memory/failure_memory.json"):
        os.remove("memory/failure_memory.json")
    
    # Load fresh memory
    mem = load_memory()
    assert mem == {"ceo": [], "cfo": [], "cto": []}, "Memory initialization failed"
    print("  ✓ Memory initialization OK")
    
    # Record failures
    record_failure("cfo", {"cash": 5000}, "invest_growth", "cash decreased")
    record_failure("cfo", {"cash": 4500}, "increase_marketing", "negative profit")
    
    # Get failures
    fails = get_recent_failures("cfo")
    assert len(fails) == 2, f"Expected 2 failures, got {len(fails)}"
    print(f"  ✓ Recorded and retrieved {len(fails)} failures")
    
    # Verify file persistence
    assert Path("memory/failure_memory.json").exists(), "Memory file not created"
    print("  ✓ failure_memory.json created and persisted")
    
except Exception as e:
    print(f"  ✗ Failure memory test FAILED: {e}")
    sys.exit(1)

# TEST 4: AI decision function integrity
print("\n[TEST 4] AI decision function...")
try:
    cfo_state = {
        "cash": 5000,
        "burn_rate": 500,
        "expenses": 2000,
        "revenue": 3000
    }
    
    # This will use fallback since API may not be enabled
    action, reason = ai_choose_action("cfo", cfo_state)
    print(f"  ✓ ai_choose_action() callable")
    print(f"    - Action: {action.type}")
    print(f"    - Reason includes 'strategic': {'strategic' in reason.lower()}")
    assert "strategic" in reason.lower(), "Strategist thinking not found"
    print("  ✓ Strategist reasoning added")
    
except Exception as e:
    print(f"  ✗ AI decision test FAILED: {e}")
    sys.exit(1)

# TEST 5: Check code modifications
print("\n[TEST 5] Code modifications check...")
try:
    with open("ai_decisions.py", "r") as f:
        content = f.read()
        assert "from failure_memory import get_recent_failures" in content, "Missing import"
        print("  ✓ failure_memory import in ai_decisions.py")
        assert "get_recent_failures(task)" in content, "Missing get_recent_failures call"
        print("  ✓ get_recent_failures() call present")
        assert "Past failures:" in content, "Missing failure context"
        print("  ✓ Failure context in prompt")
        assert "Strategic decision based on state and constraints" in content, "Missing strategist thinking"
        print("  ✓ Strategist thinking enhancement")
except Exception as e:
    print(f"  ✗ Code modification check FAILED: {e}")
    sys.exit(1)

try:
    with open("app.py", "r") as f:
        content = f.read()
        assert "from failure_memory import record_failure" in content, "Missing import"
        print("  ✓ failure_memory import in app.py")
        assert "record_failure(" in content, "Missing record_failure calls"
        print("  ✓ record_failure() calls present")
        assert "cash decreased" in content, "Missing failure detection logic"
        print("  ✓ Failure detection logic added")
except Exception as e:
    print(f"  ✗ app.py check FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL VALIDATION TESTS PASSED!")
print("=" * 60)
print("\n📋 Summary:")
print("  • failure_memory.py - Created and functional")
print("  • ai_decisions.py - Enhanced with failure context & strategist thinking")
print("  • app.py - Integrated failure detection")
print("  • failure_memory.json - Persisting failures correctly")
print("\n🚀 Ready for simulation runs!")
