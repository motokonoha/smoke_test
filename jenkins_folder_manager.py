
import os
from base import *
import argparse

workspace = os.environ['WORKSPACE']
baseline = str(os.environ['BASELINE'])

source_dir = "C:/private_teststation01"

parser = argparse.ArgumentParser()
parser.add_argument("--jenkins", help="type in ""--jenkins=path"" to handle folders ", type=str)
arguments = parser.parse_args()
if arguments.jenkins and os.path.exists(arguments.jenkins):
    source_dir = arguments.jenkins


class jenkins_folder_manager:

    def baseline_dir(self):
        configuration_file_name = 'configuration.json'
        src_configuration_file_name = os.path.join(source_dir,configuration_file_name)

        if not os.path.exists(src_configuration_file_name):
            print ('%s is not found.'%src_configuration_file_name)
            exit(-1)
        else:
            print("Copy json configuration")
            shutil.copy(src_configuration_file_name, workspace)

        with open(configuration_file_name) as config_handle:
            self.configuration = json.load(config_handle)

        self.project_name = self.configuration["project_name"]
        self.version = os.environ["Releases"]

        self.project_dir = os.path.join(workspace,self.project_name)
        self.version_dir = os.path.join(self.project_dir, self.version)
        baseline_dir = os.path.join(self.version_dir, "%s"%baseline)
        artifacts_dir = os.path.join(self.version_dir,"artifacts")

        if not os.path.exists(baseline_dir):
            print("Create ""%s\%s\%s\%s"" for flashing purpose"%(workspace,self.project_name, self.version,baseline))
            os.makedirs(baseline_dir)
        print("%s folder found, continue to copy artifacts into it"%baseline)
        shutil.move(artifacts_dir,baseline_dir)

    def workspace_dir(self):
        local_project_dir = os.path.join(source_dir,self.project_name)
        local_version_dir = os.path.join(local_project_dir,self.version)
        local_configs_dir = os.path.join(local_version_dir,"configs")

        print("Enter test_station01 to copy configuration into workspace")
        os.chdir(source_dir)

        #print("Copy json configuration")
        #shutil.copy("configuration.json",workspace)

        print("Copy codeplug s19 to workspace")
        for file in os.listdir(local_version_dir):
            if file.endswith("_cp.s19"):
                shutil.copy(os.path.join(local_version_dir,file),self.version_dir)

        print("Copy related configs to workspace")
        configs_dir = os.path.join(self.version_dir,"configs")
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