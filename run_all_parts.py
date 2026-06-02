"""Runs all three story parts sequentially by patching ACTIVE_PART each time."""
import subprocess
import sys

for part_index in range(3):
    print(f"\n{'='*60}")
    print(f"  STARTING PART {part_index + 1} OF 3")
    print(f"{'='*60}\n")

    # Patch the ACTIVE_PART line in agent.py, run it, then move on
    with open("agent.py", "r") as f:
        src = f.read()

    # Replace the active part index
    import re
    patched = re.sub(
        r"^ACTIVE_PART = \d+.*$",
        f"ACTIVE_PART = {part_index}  # 0=Part1, 1=Part2, 2=Part3",
        src,
        flags=re.MULTILINE,
    )

    with open("agent.py", "w") as f:
        f.write(patched)

    result = subprocess.run([sys.executable, "agent.py"])
    if result.returncode != 0:
        print(f"\nPart {part_index + 1} failed — stopping.")
        sys.exit(1)

print("\nAll 3 parts complete!")
