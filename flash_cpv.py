from ms import create_ms, is_ms_frodo, is_ms_aragorn, is_ms_boromir, is_ms_barney, is_ms_bsi
import unittest
import math
from time import sleep
from mot_test import MotTestCase
from create_cpv import *



class flash_cpv(MotTestCase):

    def generate_cpv(self):
        try:
            self.run_test = create_cpv()
            self.run_test.rand_uuid()
            self.run_test.create_cpv_file()
            self.new_uuid = self.run_test.new_cpv_name
        except:
            print(("[ERROR] %s")%sys.exc_info()[1])
            exit(-1)

    def __init__(self, testname, ms1_cfg = "ms1"):
        super(flash_cpv, self).__init__(testname)
        self.ms1_cfg = ms1_cfg
        self.generate_cpv()
        #self.ms2_cfg = ms2_cfg
        #self.ms3_cfg = ms3_cfg

    def setUp(self):
        self.ms1 = create_ms(self.ms1_cfg)
        #self.ms2 = create_ms(self.ms2_cfg)
        #self.ms3 = create_ms(self.ms3_cfg)

    def tearDown(self):
        self.ms1.destroy()
        #self.ms2.destroy()
        #self.ms3.destroy()

    def connect(self):
        self.ms1.Connect(async = True)
        #self.ms2.Connect(async = True)
        #self.ms3.Connect()
        self.ms1.wait()
        #self.ms2.wait()

    def _load_ms_specific_config(self, ms, ms_name, async = False):
        if is_ms_frodo(ms_name):
            ms.SetCpValuesFromCPV('ms_frodo.cpv', async = async)
        elif is_ms_aragorn(ms_name):
            ms.SetCpValuesFromCPV('ms_aragorn.cpv', async = async)
        elif is_ms_boromir(ms_name):
            ms.SetCpValuesFromCPV('ms_boromir.cpv', async = async)
        elif is_ms_barney(ms_name):
            ms.SetCpValuesFromCPV('ms_barney.cpv', async = async)

    def _load_ete_specific_config(self, ms, ms_name, async = False):
        if is_ms_bsi(ms_name):
            ms.SetCpValuesFromCPV('ete_bsi.cpv', async = async)
        else:
            ms.SetCpValuesFromCPV('ete_clean.cpv', async = async)

    def test_001_set_default_cp_parameters(self):
        self.connect()

        #load base configuration
        self.ms1.SetCpValuesFromCPV('base.cpv', async = True)
        #self.ms2.SetCpValuesFromCPV('base.cpv', async = True)
        #self.ms3.SetCpValuesFromCPV('base.cpv')
        self.ms1.wait()
        #self.ms2.wait()

        #load test environment configuration
        self.ms1.SetCpValuesFromCPV('environment.cpv', async = True)
        #self.ms2.SetCpValuesFromCPV('environment.cpv', async = True)
        #self.ms3.SetCpValuesFromCPV('environment.cpv')
        self.ms1.wait()
        #self.ms2.wait()

        #load edited CP configuration
        file_path = os.path.join(os.getcwd(),"temp")
        self.ms1.SetCpValuesFromCPV(os.path.join(file_path,"%s"%self.new_uuid), async = True)
        #self.ms2.SetCpValuesFromCPV(os.path.join(file_path,"%s"%self.new_uuid), async = True)
        #self.ms3.SetCpValuesFromCPV(os.path.join(file_path,"%s"%self.new_uuid))
        self.ms1.wait()
        #self.ms2.wait()

        #load ms specific configuration
        self._load_ms_specific_config(self.ms1, self.ms1_cfg, async = True)
        #self._load_ms_specific_config(self.ms2, self.ms2_cfg, async = True)
        #self._load_ms_specific_config(self.ms3, self.ms3_cfg)
        self.ms1.wait()
        #self.ms2.wait()

        #load ete encryption specific configuration
        self._load_ete_specific_config(self.ms1, self.ms1_cfg, async = True)
        #self._load_ete_specific_config(self.ms2, self.ms2_cfg, async = True)
        #self._load_ete_specific_config(self.ms3, self.ms3_cfg)
        self.ms1.wait()
        #self.ms2.wait()

        self.ms1.CommitCp(async = True)
        #self.ms2.CommitCp(async = True)
        #self.ms3.CommitCp()
        self.ms1.wait()
        #self.ms2.wait()


