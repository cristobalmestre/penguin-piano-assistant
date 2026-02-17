import subprocess
from config import BASE_DIR

# List of Python files to run in order (absolute paths, no os.chdir needed)
python_files = ["config_assistant.py", "graphic_interphase_for_pi.py"]

for file in python_files:
    print(f"Executing {file}")
    subprocess.run(["python3", str(BASE_DIR / file)])
    print(f"{file} executed.")
