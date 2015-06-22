__author__ = 'vcfr67'
from base import *
import pprint
import subprocess
import os

class gather_test_manager(base):
    def __init__(self):
        super(gather_test_manager,self).__init__()
        self.script_dirs = []
        self.initial_path = os.getcwd()

    def sync_test(self):
        for (script_dir, commands, sc_type) in self.get_test_repo():
            self.script_dirs.append(script_dir)
            os.chdir(script_dir)
            os.chdir(os.path.pardir)
            if sc_type and self.get_latest():
                sc_manager = self.get_source_control(sc_type)
                for command in commands:
                    command_list = [sc_manager] + command
                    print(" ".join(command_list))
                    subprocess.call(command_list)

    def copy_test_script(self):
        for script_dir in self.script_dirs:
            local_test_dir = os.path.join(self.LOCAL_BASE_LINE, os.path.basename(os.path.normpath(script_dir)))
            if os.path.exists(local_test_dir):
                shutil.rmtree(local_test_dir)
            print("%s => %s"%(script_dir, local_test_dir))
            shutil.copytree(script_dir, local_test_dir)
            script_dir = local_test_dir

if __name__ == "__main__":
    print(" >>>> Collecting test script\n")
    gather_test = gather_test_manager()
    gather_test.sync_test()
    gather_test.copy_test_script()