#!/user/grc738/python27/Python-2.7.5/bin/python
# -*- encoding: utf-8 -*-

import os
import sys
import pprint
import shutil
import glob


print(os.environ['baseline'])
print(os.environ['WORKSPACE'])
pprint.pprint(os.environ)
build_type = str(os.environ['build_type'])
baseline = str(os.environ['baseline'])
workspace = os.environ['WORKSPACE']

RELEASE = str(os.environ['Releases'])
PROJECT = "MARVEL"
ENCRYPTION = "020"
COMPUTER_NAME = "ts-09-01"
DUMP_DIR = os.path.join("easitest", "JenkinsPrivateBuild020")
BUILD = baseline
INTERNAL_BUILDS_ROOT = "proj"



sys.path.append("/%s/TetraSubscribers/%s/%s/"%(INTERNAL_BUILDS_ROOT,RELEASE, DUMP_DIR))
from jenkins_utils import *

DUMP_FILE_FOLDER = "/%s/TetraSubscribers/%s/%s"%(INTERNAL_BUILDS_ROOT,RELEASE, DUMP_DIR)
DUMP_FILE = "%s/artifacts-%s.dmp"%(DUMP_FILE_FOLDER, COMPUTER_NAME)

MAIN_DIR = "/%s/TetraSubscribers/%s/internal_builds/%s"%(INTERNAL_BUILDS_ROOT,RELEASE, BUILD)
CP_DIRS = ["/%s/TetraSubscribers/%s/CPS"%(INTERNAL_BUILDS_ROOT,RELEASE)]


MONITOR_Z19_FILES = [
"%s27%s%s\.z19$"%(build_type, ENCRYPTION, baseline),
"%s14000%s\.z19$"%(build_type,baseline),
"%s13%s%s\.z19$"%(build_type, ENCRYPTION,baseline),
"%s33%s%s\.z19$"%(build_type, ENCRYPTION,baseline)
]


MONITOR_FILES = [
"%s27%s%s_non_japanese_non_chinese\.s19$"%(build_type,ENCRYPTION,baseline),
"flashstrap-frodo-autotest\.s19$",
"%s14000%s_rech_non_japanese_non_chinese\.s19$"%(build_type,baseline),
"flashstrap_NGCH_RF\.s19$",
"ZPL03_REMOTE_OMAP_KERNEL.*\.s19$",
"\d..%s13%s%s_english\.s19$"%(build_type,ENCRYPTION,baseline),
"%s33%s%s_English\.s19$"%(build_type, ENCRYPTION,baseline),
"flashstrap-aragorn\.s19$"
]

STATIC_FILES = [
"/%s/TetraSubscribers/%s/%s/ZPL03_KRNL_PATRIOT_1.48.s19"%(INTERNAL_BUILDS_ROOT, RELEASE, DUMP_DIR),
"/%s/TetraSubscribers/%s/%s/ZPL03_SUBLOADER_1.1.s19"%(INTERNAL_BUILDS_ROOT, RELEASE, DUMP_DIR),
"/%s/TetraSubscribers/%s/%s/FLASHSTRAP_13_1.33.s19"%(INTERNAL_BUILDS_ROOT, RELEASE, DUMP_DIR)
]

UPLOADED_FILES = [
             "Frodo-(BIRD)27-020-(baseline).s19",
             "Frodo-(BIRD)32-020-(baseline).s19",
             "Aragorn-(BIRD)33-020-(baseline).s19",
             "Aragorn-(BIRD)34-020-(baseline).s19",
             "Barney-(BIRD)13-020-(baseline).s19"
             ]

ENVIRONMENT_LIST = [
    'ARAGORN-DSP= ',
    'ARAGORN-ARM= ',
    'FRODO-DSP= ',
    'FRODO-ARM= ',
    'BARNEY-ARM= '
]

BUILD_ARTIFACTS = [
	'enc=020,label=TetraSig_unix,plat=13',
	'enc=020,label=TetraSig_unix,plat=27',
	'enc=020,label=TetraSig_unix,plat=33',
]


def begin_artifact_collection():
    global RELEASE
    global DUMP_DIR
    global COMPUTER_NAME
    global DUMP_FILE
    global UPLOADED_FILES
    global ENVIRONMENT_LIST
    HISTORY_FILE = "%s/artifacts-%s-history.dmp"%(DUMP_FILE_FOLDER,COMPUTER_NAME)

    file_set = load_files_set(DUMP_FILE)
    extract_zip_files_and_copy_monitored(file_set, os.getcwd())
    update_history(os.environ.get('BUILD_NUMBER'), file_set[0], HISTORY_FILE, os.getcwd())

def set_valid_s19_into_env(s19):
    #set environment variable with the correct s19 eg os.environ["Frodo-arm"] = s19
    ara_dsp = re.compile(r"Aragorn-%s33\W"%build_type)
    ara_arm = re.compile(r"Aragorn-%s34\W"%build_type)
    fro_dsp = re.compile(r"Frodo-%s27\W"%build_type)
    fro_arm = re.compile(r"Frodo-%s32\W"%build_type)
    bar_arm = re.compile(r"Barney-%s13\W"%build_type)
    if bool(ara_dsp.search(s19)):
        ENVIRONMENT_LIST.append('ARAGORN-DSP = %s/%s/%s/artifacts/%s'%(PROJECT,RELEASE,baseline,s19))
    elif bool(ara_arm.search(s19)):
        ENVIRONMENT_LIST.append('ARAGORN-ARM = %s/%s/%s/artifacts/%s'%(PROJECT,RELEASE,baseline,s19))
    elif bool(fro_dsp.search(s19)):
        ENVIRONMENT_LIST.append('FRODO-DSP = %s/%s/%s/artifacts/%s'%(PROJECT,RELEASE,baseline,s19))
    elif bool(fro_arm.search(s19)):
        ENVIRONMENT_LIST.append('FRODO-ARM = %s/%s/%s/artifacts/%s'%(PROJECT,RELEASE,baseline,s19))
    elif bool(bar_arm.search(s19)):
        ENVIRONMENT_LIST.append('BARNEY-ARM = %s/%s/%s/artifacts/%s'%(PROJECT,RELEASE,baseline,s19))

def get_built_s19_uploaded_name(dir_name):
    if('plat=13' in dir_name):
        return os.path.join(workspace, "Barney-(BIRD)13-020-(baseline).s19")
    elif('plat=27' in dir_name):
        return os.path.join(workspace, "Frodo-(BIRD)27-020-(baseline).s19")
    elif('plat=33' in dir_name):
        return os.path.join(workspace, "Aragorn-(BIRD)33-020-(baseline).s19")
    else:
       raise Exception("Unsupported platform: %s"%(s19))

def get_valid_built_s19():
    for built_dir in BUILD_ARTIFACTS:
        full_built_dir = os.path.join(workspace, built_dir)
        if not os.path.exists(full_built_dir) or len(glob.glob(os.path.join(full_built_dir, '*-signed.s19'))) == 0:
            return False
        else:
            built_s19 = glob.glob(os.path.join(full_built_dir, '*-signed.s19'))
            if len(built_s19) > 1:
                raise Exception("More than one s19 found in the directory: %s"%(full_built_dir))
            else:
                converted_full_path_name = get_built_s19_uploaded_name(full_built_dir)
                shutil.copy(built_s19[0], converted_full_path_name)
                print("convert %s to %s"%(built_s19[0], converted_full_path_name))
    return True


def validate_and_change_custom_s19():
    #check existance
    for file_name in UPLOADED_FILES:
        if os.path.exists("%s"%file_name):
            if (os.path.getsize("%s"%file_name))> 0:
              uploaded_build_type =file_name.replace("(BIRD)",build_type)
              uploaded_s19 = uploaded_build_type.replace("(baseline)",baseline)
              set_valid_s19_into_env(uploaded_s19)
              os.rename(file_name,uploaded_s19)
              print ("Custom binary found: %s"%file_name)
    create_properties_env(ENVIRONMENT_LIST)
    #check s19 file size
    #if file size > 0
    #replace name with environment value
    #set_valid_s19_into_env()

def create_properties_env(env_list):
    #pprint.pprint(environment_list)
    with open("ATest_env.properties", 'w') as handle:
        for environment in env_list:
            handle.write(environment + "\n")

if __name__ == "__main__":
    if not os.path.exists(DUMP_FILE_FOLDER):
         os.makedirs(DUMP_FILE_FOLDER)
    if "latest" in MAIN_DIR:
         MAIN_DIR = os.path.realpath(MAIN_DIR)
         MAIN_DIR = os.sep.join(MAIN_DIR.split(os.sep)[:-1])
    new_set = get_cur_files_set(MONITOR_Z19_FILES, MONITOR_FILES, STATIC_FILES, MAIN_DIR, CP_DIRS)
    old_set = load_files_set(DUMP_FILE)
    fail_desc = are_files_set_same(old_set, new_set)
    if fail_desc:
        description_tag = "description"
        cause_tag = "cause"
        m = re.search("(\d{4}.?)$",new_set[0])
        if m:
            print("<"+description_tag+"><b><i>"+m.group(1)+"</i></b></"+description_tag+">")
        print("<"+cause_tag+">"+fail_desc+"</"+cause_tag+">")
        dump_files_set(new_set, DUMP_FILE)
    begin_artifact_collection()
    if(not get_valid_built_s19()):
        print("No Built S19 found from parent.")
        for static_file in STATIC_FILES:
            shutil.copy(static_file, workspace)
    else:
        print("Built S19 found from parent. Run test using new built S19")
    validate_and_change_custom_s19()
