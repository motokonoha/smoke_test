
#create random_uuid.cpv
#the contents is base on the informations written in configuration.json

import os
import json
import pprint
import uuid
import sys
from base import *

class create_cpv(base):

    def create_cpv_file(self):
        if "edit_cp" in self.configuration:
            file_path = os.path.join(os.getcwd(),"temp")
            with open (os.path.join(file_path,self.new_cpv_name), "w") as cpv_name :
                for line in self.configuration["edit_cp"]:
                    cpv_name.write(line)
                    cpv_name.write ("\n")
            print("%s file is created"%self.new_cpv_name)

    def rand_uuid(self):
        new_uuid = uuid.uuid4()
        self.new_cpv_name = "%s.cpv"%new_uuid




