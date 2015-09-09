from ms import create_ms, is_ms_frodo, is_ms_aragorn, is_ms_boromir, is_ms_barney, is_ms_bsi
import unittest
import math
from time import sleep
from mot_test import MotTestCase
from create_cpv import *



class flash_cpv(MotTestCase):

    def generate_cpv(self):
        try:
            test=create_cpv()
            test.get_ms_name()
        except:
            print(("[ERROR] %s")%sys.exc_info()[1])
            exit(-1)

    #TODO:make ms as a list
    def __init__(self, testname, ms1_cfg = "ms1", ms2_cfg = "ms2", ms3_cfg = "ms3"):
        super(flash_cpv, self).__init__(testname)
        self.ms_cfgs = [ms1_cfg, ms2_cfg, ms3_cfg]

    def setUp(self):
        self.ms_list = []
        for ms_cfg in self.ms_cfgs:
            ms = create_ms(ms_cfg)
            self.ms_list.append(ms)

    def tearDown(self):
        for ms in self.ms_list:
            ms.destroy()

    def connect(self):
        for ms in self.ms_list:
            ms.Connect(async = True)
            ms.wait()

    def test_001_set_default_cp_parameters(self):
        #load edited CP configuration
        self.generate_cpv()
        self.connect()
        file_path = os.path.join(os.getcwd(),"temp")
        for ms in self.ms_list:
            ms_file_path = os.path.join(file_path,"edit_%s.cpv"%ms.platform)
            if os.path.exists(ms_file_path):
                ms.SetCpValuesFromCPV(ms_file_path, async = True)

        for ms in self.ms_list:
            ms.wait()

        for ms in self.ms_list:
            ms.CommitCp(async = True)

        for ms in self.ms_list:
            ms.wait()

