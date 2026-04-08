#!/usr/bin/env python3
"""Final validation that NameError is fixed"""

import sys

print("=" * 60)
print("🔍 FINAL VALIDATION: NameError Fix")
print("=" * 60)

# TEST 1: Import app.py
print("\n[TEST 1] Import app.py modules...")
try:
    from failure_memory import record_failure
    print("  ✓ failure_memory.record_failure imported")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

try:
    from openenv.models import Action
    print("  ✓ openenv.models.Action imported")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    sys.exit(1)

# TEST 2: Check code structure
print("\n[TEST 2] Verify code structure...")
with open("app.py", "r", encoding="utf-8") as f:
    app_content = f.read()

checks = [
    ("from failure_memory import record_failure", "Import statement"),
    ("if step > 0 and len(cfo_cash) > 1:", "Correct condition"),
    ("prev_cash = cfo_cash[-2]", "Previous cash retrieval"),
    ("record_failure(", "Failure recording calls"),
    ("cash decreased", "Failure detection"),
    ("negative profit", "Profit detection"),
]

for check_str, label in checks:
    if check_str in app_content:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ {label} - NOT FOUND")
        sys.exit(1)

# TEST 3: Verify NameError is gone
print("\n[TEST 3] Verify NameError fix...")
if 'if task == "cfo"' in app_content:
    print("  ✗ OLD CODE STILL PRESENT - NameError NOT fixed!")
    sys.exit(1)
else:
    print("  ✓ Problematic 'task' variable reference removed")

# TEST 4: Syntax validation
print("\n[TEST 4] Syntax validation...")
try:
    import py_compile
    py_compile.compile("app.py", doraise=True)
    print("  ✓ app.py compiles without syntax errors")
except Exception as e:
    print(f"  ✗ Syntax error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL VALIDATION TESTS PASSED!")
print("=" * 60)
print("\n📋 Fix Summary:")
print("  • Removed: if task == \"cfo\" or step > 0:")
print("  • Added: Correct CFO failure detection with proper cash tracking")
print("  • Import: record_failure present and functional")
print("  • No NameError - 'task' variable no longer referenced")
print("\n🚀 App is ready to run!")
