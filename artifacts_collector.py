__author__ = 'vcfr67'
from base import *
import pprint
import subprocess
import sys
import re
from jenkins_utils import *
import json


class artifacts_collection(base):
    def __init__(self):
        super(artifacts_collection,self).__init__()

    def verify_version(self):
            print(self.MAIN_DIR)
            print(self.CP_DIRS)
            new_set = get_cur_files_set(self.MONITOR_Z19_FILES, self.MONITOR_FILES, self.STATIC_FILES, self.MAIN_DIR, self.CP_DIRS)
            old_set = load_files_set(self.DUMP_FILE)

            new_set_json = json.dumps(new_set, sort_keys=True)
            old_set_json = json.dumps(old_set, sort_keys=True)
            fail_desc = new_set_json != old_set_json

            if not fail_desc:
                print("Same - do not trigger")
                return False
            else:
                print("Different - trigger")
                #description_tag = "description"
                #cause_tag = "cause"
                #m = re.search("(\d{4}.?)$",new_set[0])
                #if m:
                #    print("<"+description_tag+"><b><i>"+m.group(1)+"</i></b></"+description_tag+">")
                #    print("<"+cause_tag+">"+fail_desc+"</"+cause_tag+">")
                dump_files_set(new_set, self.DUMP_FILE)
                return True

    def copy_artifacts(self):
        if not os.path.exists(self.LOCAL_DUMP_FILE):
            shutil.copyfile(self.DUMP_FILE, self.LOCAL_DUMP_FILE)
            file_set = load_files_set(self.LOCAL_DUMP_FILE)
            extract_zip_files_and_copy_monitored(file_set, self.LOCAL_ARTIFACTS_LOCATION)
        #####TODO: copy local build s19


if __name__ == "__main__":
    artifacts_collector = artifacts_collection()
    is_latest = True
    # will only verify version if dump not appear
    # This for automated test station
    if artifacts_collector.is_automated():
        print(" >>>> verify version for automated test\n")
        is_latest = artifacts_collector.verify_version()
    else:
        print(" >>>> No Automation required\n")
        artifacts_collector.verify_version()
    if is_latest:
        if artifacts_collector.require_upgrade():
            print(" >>>> collecting artifacts to %s\n"%artifacts_collector.LOCAL_ARTIFACTS_LOCATION)
            artifacts_collector.copy_artifacts()
        exit(0)
    else:
        exit(1)