__author__ = 'vcfr67'
# main entry
import subprocess
import time
import os
import sys, getopt
import pprint
from base import *

class main_runner(base):
    def __init__(self):
        super(main_runner,self).__init__()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    runner = main_runner()
    args = runner.get_arg_value_by_opt('-p')
    args += runner.get_arg_value_by_opt('--process')

    processes = [
            os.path.join(script_dir, "artifacts_collector.py"),
            os.path.join(script_dir, "flash_manager.py"),
            os.path.join(script_dir, "gather_test.py"),
            os.path.join(script_dir, "test_execution.py")
    ]
    if len(args) > 0:
        processes = []
        for process_name in args:
            process = os.path.join(script_dir, "%s.py"%(process_name))
            processes.append(process)

    for process in processes:
        cmd = ["python", process]
        if len(sys.argv) > 2:
            cmd = cmd + sys.argv[1:]
        status = subprocess.check_call(cmd)
        if status != 0:
            break
