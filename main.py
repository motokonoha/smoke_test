__author__ = 'vcfr67'
import subprocess
import time
import os

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    processes = [
        os.path.join(script_dir, "artifacts_collector.py"),
        os.path.join(script_dir, "gather_test.py"),
        os.path.join(script_dir, "flash_manager.py"),
    ]
    for process in processes:
        status = subprocess.check_call(["python", process])
        if status != 0:
            break
