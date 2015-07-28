
#create uuid.cpv
#the contents is base on the informations written in configuration.json

import os
import json
import pprint
import uuid
import sys

class create_cpv:

    def __init__(self):
        self.configuration_file_name = 'configuration.json'
        self.opts = []
        if not os.path.exists(self.configuration_file_name):
            raise Exception('%s is not found!!!!!'%self.configuration_file_name)
        with open(self.configuration_file_name) as config_handle:
            self.configuration = json.load(config_handle)

    def create_cpv_file(self):
        self.get_edit_env()
        if "edit_cp" in self.configuration:
            with open (self.NEW_CPV_NAME, "w") as CPV_NAME:
                for line in self.configuration["edit_cp"]:
                    CPV_NAME.write(line)
                    CPV_NAME.write ("\n")

    def get_edit_env(self):
        return self.configuration["edit_cp"]

    def rand_UUID(self):
        self.UUID_GEN = uuid.uuid4()
        self.NEW_CPV_NAME = "%s.cpv"%self.UUID_GEN
        print("%s file is created"%self.NEW_CPV_NAME)

    #retyrn config name
    def get_cpv_name(self):
        return self.configuration_file_name

if __name__ == "__main__":
    try:
        run_test = create_cpv()
        run_test.rand_UUID()
        run_test.create_cpv_file()
    except:
        print(("[ERROR] %s")%sys.exc_info()[1])
        exit(-1)

