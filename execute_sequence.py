import subprocess
import os

# Update the working directory
from config_assistant import new_directory
os.chdir(new_directory)

# Now the working directory has been changed
print("Working directory changed to:", os.getcwd())

# List of Python files in the desired order
python_files = ["config_assistant.py", "graphic_interphase_for_pi.py"]

for file in python_files:
    print(f"Executing {file}")
    subprocess.run(["python3", file])
    print(f"{file} executed.")
