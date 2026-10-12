import re

with open("code/eval_agent.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "[Unit Test]" in line:
        # It looks like: print("\n[Unit Test] 2. Kịch bản mục tiêu nhỏ (outline Docker) -> Dừng sớm")
        m = re.search(r"\[Unit Test\] (\d+)\.", line)
        if m:
            num = int(m.group(1))
            new_num = num - 1
            line = line.replace(f"[Unit Test] {num}.", f"[Unit Test] {new_num}.")
    new_lines.append(line)

with open("code/eval_agent.py", "w") as f:
    f.writelines(new_lines)
