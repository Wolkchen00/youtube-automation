"""Quick test: Verify all APIs work."""
from core.kie_api import check_credit
from core.script_generator import generate_script

# 1. Credit check
print("=" * 50)
print("TEST 1: Kie AI Credit Check")
credit = check_credit()
if credit:
    print(f"  Credits: {credit}")
    print(f"  USD: ${float(credit) * 0.005:.2f}")
    print("  RESULT: PASS")
else:
    print("  RESULT: FAIL")

# 2. Gemini script generation
print("\n" + "=" * 50)
print("TEST 2: Gemini Script Generation")
try:
    result = generate_script("shadowedhistory", "The Baghdad Battery")
    if result and result.get("title"):
        print(f"  Title: {result['title']}")
        print(f"  Hook: {result.get('hook', 'N/A')[:80]}")
        print("  RESULT: PASS")
    else:
        print("  RESULT: FAIL (no result)")
except Exception as e:
    print(f"  RESULT: FAIL ({e})")

print("\n" + "=" * 50)
print("All tests complete.")
