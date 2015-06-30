__author__ = 'vcfr67'
import shutil
import os
import json
import configparser
import pprint
import sys, getopt

class base:
    def __init__(self):
        self.supported_sc = {'git':[['reset', '--hard', 'HEAD'], ['pull']]}
        self.supported_sc_executable = {'git':'git'}
        self.configuration_file_name = 'configuration.json'
        self.opts = []
        if not os.path.exists(self.configuration_file_name):
            print('configuration.json is not found!!!!!')
            raise Exception('%s is not found!!!!!'%self.configuration_file_name)
        with open(self.configuration_file_name) as config_handle:
            self.configuration = json.load(config_handle)
        self.initialization()
        self.dir_initialization()

    def initialization(self):
        self._script_dirs = []
        self._configs = []

        self.DUMP_FILE_NAME = "artifacts-signaling-all.dmp"
        self.DUMP_FILE_LOCATION = os.path.join(self.get_project_name(), self.get_version())

        self.CONFIGS_LOCATION = os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION, 'configs')
        self.LOCAL_BASE_LINE = os.path.join(os.getcwd(),  self.DUMP_FILE_LOCATION, self.get_baseline())
        self.LOCAL_ARTIFACTS_LOCATION = os.path.join(self.LOCAL_BASE_LINE, "artifacts")

        self.DUMP_FILE = os.path.join(self.DUMP_FILE_LOCATION,  self.DUMP_FILE_NAME)#"%s\\%s\\artifacts-signaling-all.dmp"%(self.get_project_name(),self.get_version())
        self.LOCAL_DUMP_FILE = os.path.join(self.LOCAL_ARTIFACTS_LOCATION,  self.DUMP_FILE_NAME)

        self.MAIN_DIR = os.path.join(self.get_sw(), self.get_baseline())# "Y:\\%s\\internal_builds\\%s"%(self.get_version(), self.get_baseline())
        self.CP_DIRS = [self.get_cps()]#["Y:\\%s\\CPS"%self.get_version()]
        self.MONITOR_Z19_FILES = [
            "[BIRD]27%s.*\.z19$"%self.get_encryption(),
            "[BIRD]14000.*\.z19$",
            "[BIRD]13%s.*\.z19$"%self.get_encryption(),
            "[BIRD]33%s.*\.z19$"%self.get_encryption()
        ]
        self.MONITOR_FILES = [
            "[BIRD]27%s.*_non_chinese\.s19$"%self.get_encryption(),
            "flashstrap-frodo-autotest\.s19$",
            "[BIRD]14000.*_rech_non_japanese_non_chinese\.s19$",
            "flashstrap_NGCH_RF\.s19$",
            "ZPL03_REMOTE_OMAP_KERNEL.*\.s19$",
            "\d..[BIRD]13%s.*_english\.s19$"%self.get_encryption(),
            "[BIRD]33%s.*_English\.s19$"%self.get_encryption(),
            "[BIRD]35%s.*_English\.s19$"%self.get_encryption(),
            "flashstrap-aragorn\.s19$"
        ]
        self.STATIC_FILES = [
            os.path.join(self.DUMP_FILE_LOCATION, "ZPL03_KRNL_PATRIOT_1.48.s19"),#"%s\\%s\\ZPL03_KRNL_PATRIOT_1.48.s19"%(self.get_project_name(),self.get_version()),
            os.path.join(self.DUMP_FILE_LOCATION, "ZPL03_SUBLOADER_1.1.s19"),#"%s\\%s\\ZPL03_SUBLOADER_1.1.s19"%(self.get_project_name(),self.get_version()),
            os.path.join(self.DUMP_FILE_LOCATION, "FLASHSTRAP_13_1.32.s19")#"%s\\%s\\FLASHSTRAP_13_1.31.s19"%(self.get_project_name(),self.get_version()),
        ]

        if not os.path.exists(self.DUMP_FILE_LOCATION):
            print("%s directory is needed. please create"%(os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION)))
            exit(1)

    def dir_initialization(self):
        if not os.path.exists(self.LOCAL_BASE_LINE):
            os.mkdir(self.LOCAL_BASE_LINE)
        if not os.path.exists(self.LOCAL_ARTIFACTS_LOCATION):
            os.mkdir(self.LOCAL_ARTIFACTS_LOCATION)

    def get_test_scripts(self):
        for repo_dirs in self.configuration['test_repo']:
            for test_dir in repo_dirs:
                yield test_dir

    def get_test_repo(self):
        for repo_dirs in self.configuration['test_repo']:
            for (script_dir, source_control_type) in repo_dirs.items():
                if source_control_type:
                    if source_control_type in self.supported_sc:
                            yield (script_dir, self.supported_sc[source_control_type], source_control_type)
                    else:
                            yield (script_dir, None, None)

                else:
                    yield (script_dir, None, None)

    def get_source_control(self, sc):
        if "source_controls" in self.configuration:
            for source_control in self.configuration["source_controls"]:
                if sc in source_control:
                    return source_control[sc]
        if sc in self.supported_sc_executable:
            return self.supported_sc_executable[sc]
        return None

    def get_version(self):
        return self.configuration["version"]

    def get_encryption(self):
        return self.configuration["encryption"]

    def get_project_name(self):
        return self.configuration["project_name"]

    def get_baseline(self):
        if self.configuration["baseline"].lower() == "latest":
            return self.get_latest_directories(self.get_sw())
        else:
            return self.configuration["baseline"]

    def get_cps(self):
        if "cps" in self.configuration:
            return self.configuration["cps"]
        else:
            return os.path.join("Y:\\",self.get_version(),"CPS")

    def get_sw(self):
        if "sw" in self.configuration:
            return self.configuration["sw"]
        else:
            return os.path.join("Y:\\",self.get_version(),"internal_builds")

    def get_latest(self):
        if "latest" in self.configuration:
            return self.configuration["latest"]
        else:
            return None

    def is_automated(self):
        if "automated" in self.configuration:
            return self.configuration["automated"]
        else:
            return None

    def require_flash(self):
        if "flash" in self.configuration:
            return self.configuration["flash"]
        else:
            return None

    def get_latest_directories(self, directory):
        #get all of the directories name
        #dirs = [d for d in os.listdir(directory) if os.path.isdir(d)]
        for d in sorted(os.listdir(directory), reverse=True):
            if d.endswith("7z"):
                full_path = os.path.join(directory, os.path.splitext(d)[0])
                if os.path.isdir(full_path) and os.access(full_path, os.R_OK):
                    return full_path

    def get_config_list(self):
        for file in os.listdir(self.CONFIGS_LOCATION):
            if file.endswith('.ini'):
                config = configparser.ConfigParser()
                config.read(os.path.join(self.CONFIGS_LOCATION, file))
                yield config

    def get_radio_list(self):
        radio_list = []
        for config in self.configs:
            radio_list.append(config.get('MS', 'Name'))
        return radio_list

    # self.CPS_EXE_PATH = "C:\\Program Files (x86)\\MotorolaSolutions\\Depot CPS Plus\\Bin\\CPSPlus.exe"
    #self.CPS_FILE_STORAGE = "C:\\Program Files (x86)\\Motorola\\EasiTest\\RadioController\\Cache\\CodeplugCache"

    def get_cps_exe_path(self):
        if "cps_executable_path" in self.configuration:
            return self.configuration["cps_executable_path"]
        else:
            return "C:\\Program Files (x86)\\MotorolaSolutions\\Depot CPS Plus\\Bin\\CPSPlus.exe"

    def get_cps_file_storage(self):
        if "cps_storage_path" in self.configuration:
            return self.configuration["cps_storage_path"]
        else:
            return "C:\\Program Files (x86)\\Motorola\\EasiTest\\RadioController\\Cache\\CodeplugCache"

    def get_tetra_flashing_dir(self):
        if "TETRA_MS_Flashing_Tools" in self.configuration:
            return self.configuration["TETRA_MS_Flashing_Tools"]
        else:
            return "C:\\Program Files\\TETRA MS Flashing Tools"

    def get_arg_value_by_opt(self, option):
        arguments = []
        for opt, arg in self.opts:
            if opt == option:
                arguments.append(arg)
        return arguments

    def set_arg_options(self, arguments, short_options, long_options ):
        try:
            self.opts, self.args = getopt.getopt(arguments, short_options, long_options)
        except getopt.GetoptError:
            print(getopt.GetoptError.msg)
            sys.exit(2)
    @property
    def script_dirs(self):
        return self._script_dirs

    @script_dirs.setter
    def script_dirs(self, dir):
        self._script_dirs = dir

    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, configs):
        self._configs = configs







