__author__ = 'vcfr67'

from base import *
import pprint
import subprocess
import sys
import re
import os
from jenkins_utils import *
import glob
import xml.etree.cElementTree as ET
from multiprocessing import Pool
import fnmatch

from ms import *
from create_cpv import *


class test_management(base):
   def __init__(self):
       self.run_test = None

   def generate_cpv(self):
        try:
            self.run_test = create_cpv()
            self.run_test.rand_UUID()
            self.run_test.create_cpv_file()
        except:
            print(("[ERROR] %s")%sys.exc_info()[1])
            exit(-1)


   def flash_cpv(self):
       if self.run_test:
           filename = self.run_test.get_cpv_name()

   def execute_test(self):
       pass




if __name__ == "__main__":
    test_executor = test_management()
    test_executor.generate_cpv()
    test_executor.flash_cpv()
    test_executor.execute_test()
    exit(0)
