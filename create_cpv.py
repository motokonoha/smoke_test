#create random_uuid.cpv
#the contents is base on the informations written in configuration.json

import os
import json
import pprint
import uuid
import sys
from base import *
import shutil

class create_cpv(base):

   def get_ms_name(self):
       for config in self.get_config_list():
           ms_name = config.get('MS', 'Name')
           if ms_name == "Frodo":
               self.create_cpv_file(ms_name)
           elif ms_name == "Aragorn":
               self.create_cpv_file(ms_name)
           elif ms_name == "Barney":
               self.create_cpv_file(ms_name)
           else:
               print ("ERROR: NO RADIO NAME IS FOUND")

   def create_cpv_file(self,ms_name):
       if "edit_cp" in self.configuration:
            file_path = os.path.join(os.getcwd(),"temp")
            new_cpv_name = "edit_%s.cpv"%(ms_name)
            for i in range(len(self.configuration["edit_cp"])):
                if "all" in self.configuration["edit_cp"][i]:
                    with open (os.path.join(file_path,new_cpv_name), "a") as cpv_name :
                        for line in self.configuration["edit_cp"][i]["all"]:
                            cpv_name.write(line)
                            cpv_name.write ("\n")
                if ms_name in self.configuration["edit_cp"][i]:
                    with open (os.path.join(file_path,new_cpv_name), "a") as cpv_name :
                        for line in self.configuration["edit_cp"][i]["%s"%ms_name]:
                            cpv_name.write(line)
                            cpv_name.write ("\n")

