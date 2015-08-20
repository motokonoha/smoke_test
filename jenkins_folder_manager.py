
import os
from base import *
import argparse

workspace = os.environ['WORKSPACE']
baseline = str(os.environ['BASELINE'])
BDBOS_DIR = os.path.join(workspace,"BDBOS")
MR151_DIR = os.path.join(BDBOS_DIR,"MR151")

source_dir = "C:/private_teststation01"

parser = argparse.ArgumentParser()
parser.add_argument("--jenkins", help="type in ""--jenkins=path"" to handle folders ", type=str)
arguments = parser.parse_args()
if arguments.jenkins and os.path.exists(arguments.jenkins):
    source_dir = arguments.jenkins


class jenkins_folder_manager:

    def baseline_dir(self):
        baseline_dir = os.path.join(MR151_DIR, "%s"%baseline)
        artifacts_dir = os.path.join(MR151_DIR,"artifacts")
        if not os.path.exists(baseline_dir):
            print("Create ""%s\BDBOS\MR151\%s"" for flashing purpose"%(workspace,baseline))
            os.makedirs(baseline_dir)
        print("%s folder found, continue to copy artifacts into it"%baseline)
        shutil.move(artifacts_dir,baseline_dir)

    def workspace_dir(self):
        local_bdbos_dir = os.path.join(source_dir,"BDBOS")
        local_mr151_dir = os.path.join(local_bdbos_dir,"MR151")
        local_configs_dir = os.path.join(local_mr151_dir,"configs")

        print("Enter test_station01 to copy configuration into workspace")
        os.chdir(source_dir)

        print("Copy json configuration")
        shutil.copy("configuration.json",workspace)

        print("Copy codeplug s19 to workspace")
        for file in os.listdir(local_mr151_dir):
            if file.endswith("_cp.s19"):
                shutil.copy(os.path.join(local_mr151_dir,file),MR151_DIR)

        print("Copy related configs to workspace")
        configs_dir = os.path.join(MR151_DIR,"configs")
        if not os.path.exists(configs_dir):
            print("configs not found, creating one now")
            os.makedirs(configs_dir)
        for file in os.listdir(local_configs_dir):
            shutil.copy(os.path.join(local_configs_dir,file),configs_dir)

        print("Enter workspace and begin flashing")
        os.chdir(workspace)

if __name__ == "__main__":
    jenkins = jenkins_folder_manager()
    jenkins.baseline_dir()
    jenkins.workspace_dir()