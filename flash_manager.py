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

class ms_base(base):
    def __init__(self, config, flashing_path, artifact_path):
        super(ms_base,self).__init__()
        self._config = config
        assert("FLASHING" in self._config)
        self._root = None
        self._flashing_path = flashing_path
        self._artifact_path = artifact_path
        self.artifact_list = {
            "rpk" : None,
            "flashstrap" : None,
            "sw" : None,
            "cp" : "%s_cp.s19"%(config.get('MS', 'Name')),
            "cps" : ".*\\.cps"
        }

    def generate_flashing_config(self):
        cp_size = self.get_size()
        cp_blocks = self.get_blocks()
        self._root = ET.Element("conf")
        ET.SubElement(self._root, "cps").text = self.get_cps_exe_path()
        ET.SubElement(self._root, "cps_files_storage").text = self.get_cps_file_storage()
        self.ms_elements =  ET.SubElement(self._root, self._config.get('MS', 'Name'))
        ET.SubElement(self.ms_elements, "rpk", type="pattern").text = self.artifact_list["rpk"]
        ET.SubElement(self.ms_elements, "flashstrap", type="file").text = self.artifact_list["flashstrap"]
        ET.SubElement(self.ms_elements, "software", type="pattern").text = self.artifact_list["sw"]
        if cp_size and cp_blocks:
             ET.SubElement(self.ms_elements, "cp", type="file", size=cp_size, blocks=cp_blocks).text = self.artifact_list["cp"]
        else:
            ET.SubElement(self.ms_elements, "cp", type="file").text = self.artifact_list["cp"]

    def dump_xml(self):
        dest = os.path.join(self._flashing_path, self._config.get('MS', 'Name')) + ".xml"
        tree = ET.ElementTree(self._root)
        tree.write(dest)
        print("%s configuration is generated"%(dest))


    def copy_artifacts(self, artifact_list = None):
        flist = []
        if not artifact_list:
            artifact_list = self.artifact_list
        for (type, pattern) in artifact_list.items():
            for fname in os.listdir(self._artifact_path):
                if re.match(pattern, fname):
                    flist.append(fname)
        pprint.pprint(flist)
        print("\n\n")
        for fname in flist:
            src = os.path.join(self._artifact_path, fname)
            dest = os.path.join(self._flashing_path, fname)
            if not os.path.exists(dest):
                shutil.copy(src, dest)

    def generate_cp(self):
        raise Exception("read_cp is not implemented")

    def get_blocks(self):
        if "BLOCKS" in self._config["FLASHING"]:
            return self._config["FLASHING"]["BLOCKS"]
        else:
            return None

    def get_size(self):
        if "SIZE" in self._config["FLASHING"]:
            return self._config["FLASHING"]["SIZE"]
        else:
            return None

class frodo(ms_base):
    def __init__(self, config, flashing_path, artifact_path, encryption):
        super(frodo,self).__init__(config, flashing_path, artifact_path)
        self.artifact_list["rpk"] = ".*NGM.*rpk"
        self.artifact_list["flashstrap"] = "flashstrap-frodo-autotest..*"
        self.artifact_list["sw"] = "[BDIR]27%s.*_non_japanese_non_chinese\\.s19"%(encryption)
        self.artifact_list["cp"] = "%s_Brick_cp.s19"%(config.get('MS', 'Name'))

        self.CH_artifact_list = {
            "rpk" : ".*CH.*rpk",
            "flashstrap" :  "flashstrap_NGCH_RF\\.s19",
            "sw" : "[BDIR]14.*\\.s19",
            "cp" : "%s_CH_cp.s19"%(config.get('MS', 'Name')),
            "kernel" : "ZPL03_REMOTE_OMAP_KERNEL_.*\\.s19"
        }

    def copy_artifacts(self):
            super(frodo, self).copy_artifacts(self.artifact_list)
            super(frodo, self).copy_artifacts(self.CH_artifact_list)

    def generate_common_field_in_config(self, subElement, artifact_list, cp_size = None, cp_blocks = None):
         ET.SubElement(subElement, "rpk", type="pattern").text = artifact_list["rpk"]
         ET.SubElement(subElement, "flashstrap", type="pattern").text = artifact_list["flashstrap"]
         ET.SubElement(subElement, "software", type="pattern").text = artifact_list["sw"]
         if cp_size and cp_blocks:
             ET.SubElement(subElement, "cp", type="file", size=cp_size, blocks=cp_blocks).text = artifact_list["cp"]
         else:
            ET.SubElement(subElement, "cp", type="file").text = artifact_list["cp"]


    def generate_flashing_config(self):
        self._root = ET.Element("conf")
        ET.SubElement(self._root, "cps").text = self.get_cps_exe_path()
        ET.SubElement(self._root, "cps_files_storage").text = self.get_cps_file_storage()
        self.ms_elements =  ET.SubElement(self._root, "FrodoSerial")

        brick = ET.SubElement(self.ms_elements, "Brick")
        ch = ET.SubElement(self.ms_elements, "Head")

        if "PORT_APP_BRICK" in self._config["FLASHING"]:
            ET.SubElement(brick, "port").text = self._config["FLASHING"]["PORT_APP_BRICK"]
            self.generate_common_field_in_config(brick, self.artifact_list)
        else:
            raise Exception("PORT_APP_BRICK is not found under FLASHING in the INI")
        if "PORT_APP_CH" in self._config["FLASHING"]:
            ET.SubElement(ch, "port").text = self._config["FLASHING"]["PORT_APP_CH"]
            self.generate_common_field_in_config(ch, self.CH_artifact_list, "131072", "6")
            ET.SubElement(ch, "kernel", type="pattern").text = self.CH_artifact_list["kernel"]
        else:
            raise Exception("PORT_APP_CH is not found under FLASHING in the INI")
        self.dump_xml()





class aragorn(ms_base):
    def __init__(self, config, flashing_path, artifact_path, encryption):
        super(aragorn,self).__init__(config, flashing_path, artifact_path)
        self.artifact_list["rpk"] = "\\d{4}(-\\d{2})?_NGP\\.rpk"
        self.artifact_list["flashstrap"] = "flashstrap-aragorn.s19"
        self.artifact_list["sw"] = "[BDIR]33%s.*_English\\.s19"%(encryption)

    def generate_flashing_config(self):
        super(aragorn, self).generate_flashing_config()
        if "PORT_APP" in self._config["FLASHING"]:
            ET.SubElement(self.ms_elements, "port_app").text = self._config["FLASHING"]["PORT_APP"]
        else:
            raise Exception("PORT_APP is not found under FLASHING in the INI")
        if "PORT_FLASH" in self._config["FLASHING"]:
            ET.SubElement(self.ms_elements, "port").text = self._config["FLASHING"]["PORT_FLASH"]
        else:
            raise Exception("PORT_FLASH is not found under FLASHING in the INI")
        self.dump_xml()


class barney(ms_base):
    def __init__(self, config, flashing_path, artifact_path, encryption):
        super(barney,self).__init__(config, flashing_path, artifact_path)
        self.artifact_list["rpk"] = "\\d{4}(-\\d{2})?_PTB\\.rpk"
        self.artifact_list["flashstrap"] = "FLASHSTRAP_13.*\\.s19"
        self.artifact_list["sw"] = "[BDIR]13%s.*_english\\.s19"%(encryption)
        self.artifact_list["kernel"] = "ZPL03_KRNL_PATRIOT_.*\\.s19"
        self.artifact_list["loader"] = "ZPL03_SUBLOADER_.*\\.s19"

    def generate_flashing_config(self):
        super(barney, self).generate_flashing_config()
        if "PORT_APP" in self._config["FLASHING"]:
            ET.SubElement(self.ms_elements, "port").text = self._config["FLASHING"]["PORT_APP"]
        else:
            raise Exception("PORT_APP is not found under FLASHING in the INI")
        ET.SubElement(self.ms_elements, "kernel", type="pattern").text =  self.artifact_list["kernel"]
        ET.SubElement(self.ms_elements, "loader", type="pattern").text =  self.artifact_list["loader"]
        self.dump_xml()

class flash_management(base):
    def __init__(self):
        super(flash_management,self).__init__()
        for config in self.get_config_list():
            self.configs.append(config)

    def prepare_artifacts(self):
        pool = Pool()
        pool.map(self.move_require_flashing_artifacts, self.configs)
        pool.close()
        pool.join()


    def move_require_flashing_artifacts(self, config):
        ## create directory base on configs
        ms_name = config.get('MS', 'Name')
        ms_local_dir = os.path.join(self.LOCAL_BASE_LINE,ms_name)
        if not os.path.exists(ms_local_dir):
            os.mkdir(ms_local_dir)
            print("Creating directory: %s"%ms_name)
        else:
            print("directory: %s already exists"%ms_name)
        ms = None
        if ms_name == "Frodo":
            ms = frodo(config, ms_local_dir, self.LOCAL_ARTIFACTS_LOCATION, self.get_encryption())
        elif ms_name == "Aragorn":
            ms = aragorn(config, ms_local_dir, self.LOCAL_ARTIFACTS_LOCATION, self.get_encryption())
        elif ms_name == "Barney":
            ms = barney(config, ms_local_dir, self.LOCAL_ARTIFACTS_LOCATION, self.get_encryption())
        else:
            print('Unrecognized radio')
        if ms:
            #ms.copy_artifacts()
            ms.generate_flashing_config()




if __name__ == "__main__":
    flash_manager = flash_management()
    if not os.path.exists(flash_manager.CONFIGS_LOCATION):
        print("%s directory not found"%(flash_manager.CONFIGS_LOCATION))
        exit(1)
    if flash_manager.require_flash():
        print(" >>>> Begin flashing\n")
        flash_manager.prepare_artifacts()
    exit(0)
