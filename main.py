__author__ = 'vcfr67'
# main entry
import subprocess
import time
import os
import sys, getopt
import pprint

opts = []
args = []
def get_arg_value_by_opt(option):
    arguments = []
    for opt, arg in opts:
        if opt == option:
            arguments.append(arg)
    return arguments

def set_arg_options(arguments, short_options, long_options ):
        global opts
        global args
        try:
            opts, args = getopt.getopt(arguments, short_options, long_options)
        except getopt.GetoptError:
            print(getopt.GetoptError.msg)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    set_arg_options(sys.argv[1:], 'p:', ['process='])
    args = get_arg_value_by_opt('-p')
    args += get_arg_value_by_opt('--process')

    processes = [
            os.path.join(script_dir, "artifacts_collector.py"),
            os.path.join(script_dir, "gather_test.py"),
            os.path.join(script_dir, "flash_manager.py")
            # os.path.join(script_dir, "test_execution.py")
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
