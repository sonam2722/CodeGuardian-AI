import subprocess
import sys


def run_pylint(file_path):
    result = subprocess.run(
        [sys.executable, "-m", "pylint", str(file_path)],
         capture_output=True,
         text=True
)
    
    return result.stdout + result.stderr