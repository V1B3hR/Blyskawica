import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "adaptiveneuralnetwork"

# Mapping of file name (without .py) to its new directory name
mapping = {
    "sensory_hub": "peripheral_nervous_system",
    "social_comm": "peripheral_nervous_system",
    "social_learning": "peripheral_nervous_system",
    "diamond_yantra": "cognitive_tools",
    "polymathic_hub": "cognitive_tools",
    "ground_loop_isolator": "cognitive_tools",
    "wolf_teeth": "immune_system",
    "epistemic_defense": "immune_system",
    "trust_network": "immune_system",
    "robustness_validator": "immune_system"
}

def get_target_dir(mod_name):
    return mapping.get(mod_name, "central_nervous_system")

for py_file in BASE_DIR.rglob("*.py"):
    if "venv_orbital" in py_file.parts or "core_backup" in py_file.parts:
        continue

    with open(py_file, encoding='utf-8') as f:
        content = f.read()

    original = content

    # Replace "..core.mod" with "..target_dir.mod" or absolute if needed
    # Actually, easiest is just to replace "..core.xxx" with "adaptiveneuralnetwork.target_dir.xxx"
    # Or simply:
    def repl_dotdotcore(match):
        mod = match.group(1)
        tdir = get_target_dir(mod)
        # return f"adaptiveneuralnetwork.{tdir}.{mod}" # This changes relative to absolute! Safe.
        return f"adaptiveneuralnetwork.{tdir}.{mod}"

    content = re.sub(r"\.\.core\.([a-zA-Z0-9_]+)", repl_dotdotcore, content)

    # Replace "core.mod" with "adaptiveneuralnetwork.target_dir.mod"
    def repl_core(match):
        mod = match.group(1)
        tdir = get_target_dir(mod)
        return f"adaptiveneuralnetwork.{tdir}.{mod}"

    content = re.sub(r"from core\.([a-zA-Z0-9_]+)", lambda m: f"from adaptiveneuralnetwork.{get_target_dir(m.group(1))}.{m.group(1)}", content)
    content = re.sub(r"import core\.([a-zA-Z0-9_]+)", lambda m: f"import adaptiveneuralnetwork.{get_target_dir(m.group(1))}.{m.group(1)}", content)

    if content != original:
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {py_file.name}")
