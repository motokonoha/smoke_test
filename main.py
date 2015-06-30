__author__ = 'vcfr67'
# main entry
import subprocess
import time
import os
import sys

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    processes = [
        os.path.join(script_dir, "artifacts_collector.py"),
        os.path.join(script_dir, "gather_test.py"),
        os.path.join(script_dir, "flash_manager.py"),
        os.path.join(script_dir, "test_execution.py")
    ]
    for process in processes:
        cmd = ["python", process]
        if len(sys.argv) > 2:
            cmd = cmd + sys.argv[2:]
        status = subprocess.check_call(cmd)
        if status != 0:
            break
