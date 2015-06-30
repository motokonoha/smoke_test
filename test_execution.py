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



class test_management(base):
   def generate_xml(self):
       pass

   def flash_cpv(self):
       pass

   def execute_test(self):
       pass




if __name__ == "__main__":
    test_executor = test_management()
    test_executor.generate_xml()
    test_executor.flash_cpv()
    test_executor.execute_test()
    exit(0)
