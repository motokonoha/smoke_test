__author__ = 'vcfr67'
import shutil
import os
import json
import configparser
import pprint
import sys, getopt
import re
from multiprocessing import *
import unittest
import HTMLTestRunner
import time
import subprocess
import xmlrunner
from datetime import datetime
import zipfile

class base:
    def __init__(self):
        self.opts = []
        self.set_arg_options(sys.argv[1:], 'i:b:e:h:p:f:v',
                             ['merge','version=','prerun=','ignore=', 'dsp=', 'arm=', 'baseline=', 'rerun=',
                              'encryption=', 'upgrade','xml=','html=','cfgs=','logs=','whitelist=','help','cpv',
                              'process=', 'run=' , 'file_path='])
        self.supported_sc = {'git':[['reset', '--hard', 'HEAD'], ['pull']]}
        self.supported_sc_executable = {'git':'git'}
        configuration_file_name = 'configuration.json'

        if not os.path.exists(configuration_file_name):
            print ('%s is not found!!!!!'%configuration_file_name)
            exit(-1)
        with open(configuration_file_name) as config_handle:
            self.configuration = json.load(config_handle)
        self.initialization()
        self.dir_initialization()


    def initialization(self):
        self._script_dirs = []
        self._configs = []
        self.script_dirs = []
        self.DUMP_FILE_NAME = "artifacts-signaling-all.dmp"
        self.DUMP_FILE_LOCATION = os.path.join(self.get_project_name(), self.get_version())
        cfgs = os.environ.get["PYEASITEST_CFGS"]
        if cfgs:
            self.CONFIGS_LOCATION = cfgs
        else:
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
            os.path.join(self.DUMP_FILE_LOCATION, "FLASHSTRAP_13_1.33.s19")#"%s\\%s\\FLASHSTRAP_13_1.31.s19"%(self.get_project_name(),self.get_version()),
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
        if len(self.get_arg_value_by_opt("-v")) > 0:
            return self.get_arg_value_by_opt("-v")[0]
        elif len(self.get_arg_value_by_opt("--version")) > 0:
            return self.get_arg_value_by_opt("--version")[0]
        elif "Releases" in os.environ:
            return os.environ["Releases"]
        else:
            return self.configuration["version"]

    def get_encryption(self):
        if len(self.get_arg_value_by_opt("-e")) > 0:
            return self.get_arg_value_by_opt("-e")[0]
        elif len(self.get_arg_value_by_opt("--encryption")) > 0:
            return self.get_arg_value_by_opt("--encryption")[0]
        else:
            return self.configuration["encryption"]

    def get_project_name(self):
        return self.configuration["project_name"]

    def get_baseline(self):
        if len(self.get_arg_value_by_opt("-b")) > 0:
            return self.get_arg_value_by_opt("-b")[0]
        elif len(self.get_arg_value_by_opt("--baseline")) > 0:
            return self.get_arg_value_by_opt("--baseline")[0]
        elif self.configuration["baseline"].lower() == "latest":
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

    def require_upgrade(self):
        if len(self.get_arg_value_by_opt('--upgrade')) > 0:
            return self.get_arg_value_by_opt('--upgrade')
        elif "upgrade" in self.configuration:
            return self.configuration["upgrade"]
        else:
            return None


    def is_automated(self):
        if "automated" in self.configuration:
            return self.configuration["automated"]
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

    def get_filename(self):
        for i in range(len(self.configuration["whitelist"])):
            if (len(self.configuration["whitelist"][i])) == 1:
                yield self.configuration["whitelist"][i]["file_name"]

    def get_class(self):
        for i in range(len(self.configuration["whitelist"])):
            if (len(self.configuration["whitelist"][i])) == 2:
                file_name = self.configuration["whitelist"][i]["file_name"]
                class_name = self.configuration["whitelist"][i]["class_name"]
                yield(file_name, class_name)

    def get_function(self):
        for i in range(len(self.configuration["whitelist"])):
            if (len(self.configuration["whitelist"][i])) == 3:
                file_name = self.configuration["whitelist"][i]["file_name"]
                class_name = self.configuration["whitelist"][i]["class_name"]
                function_name = self.configuration["whitelist"][i]["function_name"]
                yield(file_name,class_name,function_name)

    def verify_filename(self, file_name, que, script_path):
        filename_to_verify = "%s.py"%file_name
        if script_path:
            self.cur_dir = script_path
        else:
            self.cur_dir = os.path.dirname(os.path.realpath(__file__)) #may change, depend on test file location
        for file in os.listdir(self.cur_dir):
            if file == filename_to_verify:
                print("---->%s file is found"%filename_to_verify)
                que.put(True)
                break
        else:
            print("---->%s.py file NOT FOUND!"%file_name)
            que.put(False)
            exit(-1)

    def verify_class(self,file_name, class_name, que ,script_path):
        self.verify_filename(file_name,que,script_path)
        with open(os.path.join(self.cur_dir,"%s.py"%file_name),'r') as cur_file:
            for line in cur_file:
                regex = re.compile(r"class\s%s\W"%class_name)
                match_result= bool(regex.search(line))
                if match_result == True:
                    print("---->%s class is found"%class_name)
                    que.put(True)
                    break
            if not match_result:
                print("---->%s class NOT FOUND!"%class_name)
                que.put(False)
                exit(-1)


    def verify_function(self, file_name, class_name, function_name, que,script_path):
        self.verify_class(file_name,class_name,que,script_path)
        with open(os.path.join(self.cur_dir,"%s.py"%file_name)) as cur_file:
            for line in cur_file:
                regex = re.compile(r"def\s%s\W"%function_name)
                match_result = bool(regex.search(line))
                if match_result == True:
                    print ("---->%s method is found"%function_name)
                    que.put(True)
                    break
            if not match_result:
                print("---->%s function NOT FOUND!"%function_name)
                que.put(False)
                exit(-1)

    def create_whitelist(self,script_path=None):
        self.processes = []
        for file_name in self.get_filename():
            process = "%s"%file_name
            self.processes.append(process)

        for (file_name, class_name) in self.get_class():
            process = "%s.%s"%(file_name,class_name)
            self.processes.append(process)

        for (file_name, class_name, function_name) in self.get_function():
            process = "%s.%s.%s"%(file_name,class_name,function_name)
            self.processes.append(process)
        return(self.processes)

    def create_xml_report(self, suite, xml):
        output = xml
        xmlrunner.XMLTestRunner(verbosity=2, per_test_output=True, output=output, outsuffix="out").run(suite)
        print ("XML report is created as %s"%output)

    def create_html_report(self, suite, html, test):
        with open (os.path.join(html,"TEST-" + test + ".html"), 'wb') as buf:
                runner = HTMLTestRunner.HTMLTestRunner(
                stream = buf,
                verbosity=2,
                title = "HTML Testing",
                description= 'This is the overall result of all tests.'
                )
                runner.run(suite)
        print ("HTML report is created as %s"%html)


    def generate_unittest_list(self, list):
        result = []
        for index in list:
            result.append(unittest.TestLoader().loadTestsFromName("%s"%index))
        return result

    def argument_unittest_list(self, list_of_filename):
        result = re.split(',',list_of_filename)
        return result

    def is_whitelist_available(self):
        if self.configuration:
            if len(self.configuration["whitelist"]) > 0:
                return True
        return False

    def get_time_elapsed(self, startTime):
        timestamp = datetime.now() - startTime
        print("Time Elapsed: %s"%timestamp)

    def get_radio_code(self, ms_name, type):
        radio_code_type = None
        if ms_name.lower() == 'frodo':
            if 'arm' in type:
                radio_code_type = '32'
            elif 'dsp' in type:
                radio_code_type = '27'
            else:
                raise Exception('Unknown Type: %s'%(type))
            pass
        elif ms_name.lower() == 'aragorn':
            if 'arm' in type:
                radio_code_type = '34'
            elif 'dsp' in type:
                radio_code_type = '33'
            else:
                raise Exception('Unknown Type: %s'%(type))
        elif ms_name.lower() == 'barney':
            if 'arm' in type:
                radio_code_type = '13'
            else:
                raise Exception('Unknown Type: %s'%(type))
        else:
            raise Exception("%s unknown"%(ms_name))
        return radio_code_type


    def sync_test(self):
        for (script_dir, commands, sc_type) in self.get_test_repo():
            self.script_dirs.append(script_dir)
            origin_dir = os.getcwd()
            if sc_type and self.require_upgrade():
                os.chdir(script_dir)
                os.chdir(os.path.pardir)
                sc_manager = self.get_source_control(sc_type)
                for command in commands:
                    command_list = [sc_manager] + command
                    print(" ".join(command_list))
                    subprocess.call(command_list)
            os.chdir(origin_dir)

    def copy_test_script(self):
        for script_dir in self.script_dirs:
            local_test_dir = os.path.join(self.LOCAL_BASE_LINE, os.path.basename(os.path.normpath(script_dir)))
            if os.path.exists(local_test_dir):
                shutil.rmtree(local_test_dir)
            print("%s => %s"%(script_dir, local_test_dir))
            shutil.copytree(script_dir, local_test_dir)
            yield local_test_dir
    def zipper(self, dir, zip_file):
        zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
        root_len = len(os.path.abspath(dir))
        for root, dirs, files in os.walk(dir):
            archive_root = os.path.abspath(root)[root_len:]
            for f in files:
                fullpath = os.path.join(root, f)
                archive_name = os.path.join(archive_root, f)
                zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
        zip.close()
        return zip_file

