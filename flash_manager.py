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


class ms_base(base):
    def __init__(self, config, flashing_path, artifact_path):
        super(ms_base,self).__init__()
        self._config = config
        self.Blocks = None
        self.Size = None

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
        self.flash_com = None

    def generate_flashing_config(self):
        cp_size = self.get_size()
        cp_blocks = self.get_blocks()
        self._root = ET.Element("conf")
        ET.SubElement(self._root, "cps").text = self.get_cps_exe_path()
        ET.SubElement(self._root, "cps_files_storage").text = self.get_cps_file_storage()
        self.ms_elements =  ET.SubElement(self._root, self._config.get('MS', 'Name'))
        ET.SubElement(self.ms_elements, "rpk", type="pattern").text = self.artifact_list["rpk"]
        ET.SubElement(self.ms_elements, "flashstrap", type="pattern").text = self.artifact_list["flashstrap"]
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

    def preparing_cp(self):
        if not os.path.exists(os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION, self.artifact_list["cp"])):
            if "PORT_APP" in self._config["FLASHING"]:
                self.flash_com =  self._config["FLASHING"]["PORT_APP"]
                cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-f", self.flash_com]
                print("Entering flashing mode: %s"%" ".join(cmd))
                status = subprocess.check_call(cmd)
                return status
            else:
                raise Exception("PORT_APP is not found under FLASHING in the INI")

    def set_blocks_and_size(self, flash_com):
        cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-c", str(flash_com)]
        print("Executing %s"%" ".join(cmd))
        output = str(subprocess.check_output(cmd))
        output_list = output.split('\n')
        output_array = []
        for out in output_list:
            output_array += out.split("\\r\\n")
        for output_text in output_array:
            if "Flash Block Size" in output_text:
                self.Size = output_text.split(":")[1].strip()
                print("Size: %s"%self.Size)
            if "Number of Flash Block for CodePlug" in output_text:
                self.Blocks = output_text.split(":")[1].strip()
                print("Blocks: %s"%self.Blocks)

    def generate_cp(self, dest = None):
        status = 0
        if dest == None:
            dest = os.path.join(self._flashing_path, self.artifact_list["cp"])
        existing_cp = os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION, self.artifact_list["cp"])
        if not os.path.exists(existing_cp):
            self.flash_com = self._config["FLASHING"]["PORT_APP"]
            if "PORT_FLASH" in  self._config["FLASHING"]:
                self.flash_com  = self._config["FLASHING"]["PORT_FLASH"]
            self.set_blocks_and_size(self.flash_com)
            cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-r", str(self.flash_com),  dest]
            print("Executing %s"%" ".join(cmd))
            status = subprocess.check_call(cmd)
            if status == 0:
                cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-R", str(self.flash_com)]
                print("Executing %s"%" ".join(cmd))
                status = subprocess.check_call(cmd)
        else:
            if os.path.exists(dest):
                os.remove(dest)
            shutil.copy(existing_cp, dest)
        return status

    def get_blocks(self):
        if "BLOCKS" in self._config["FLASHING"]:
            return self._config["FLASHING"]["BLOCKS"]
        else:
            return self.Blocks

    def get_size(self):
        if "SIZE" in self._config["FLASHING"]:
            return self._config["FLASHING"]["SIZE"]
        else:
            return self.Size

    def get_ms_name(self):
        return self._config.get('MS', 'Name')

    def get_files(self, dir, extension):
        matches = []
        for root, dirnames, filenames in os.walk(dir):
            for filename in fnmatch.filter(filenames, extension):
                matches.append(os.path.join(root, filename))
        return matches

    def begin_flash(self):
        #os.chdir(self._flashing_path)
        print("chdir to "+self._flashing_path)
        matches = self.get_files(self._flashing_path, '*.xml')
        flash_script = os.path.join(self.get_tetra_flashing_dir(), "flash.py")
        print(self._flashing_path)
        print(matches[0])
        status = -1
        if len(matches) == 1:
            if os.path.exists(flash_script):
                cmd = ['python',flash_script,'-c', os.path.join(self._flashing_path, os.path.basename(matches[0])), "-d", self._flashing_path, "--logdir", os.path.join(self._flashing_path, "LOGS")]
                print(" ".join(cmd))
                status = subprocess.check_call(cmd)
            else:
                 print("%s not found, probably not installed"%(flash_script ))
        else:
            print("unable to call due to multiple xml files or xml file not found!!!!")
        #os.chdir(os.getcwd())
        return status


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

        self.brick_com = None
        self.in_flash_mode = False

    def copy_artifacts(self):
            super(frodo, self).copy_artifacts(self.artifact_list)
            super(frodo, self).copy_artifacts(self.CH_artifact_list)

    def generate_common_field_in_config(self, subElement, artifact_list, cp_size = None, cp_blocks = None):
         ET.SubElement(subElement, "rpk", type="pattern").text = artifact_list["rpk"]
         ET.SubElement(subElement, "flashstrap", type="pattern").text = artifact_list["flashstrap"]
         ET.SubElement(subElement, "software", type="pattern").text = artifact_list["sw"]
         cp_path = os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION, artifact_list["cp"])
         if cp_size and cp_blocks:
             if os.path.exists(cp_path):
                ET.SubElement(subElement, "cp", type="file", size=cp_size, blocks=cp_blocks).text = cp_path
             else:
                ET.SubElement(subElement, "cp", type="file", size=cp_size, blocks=cp_blocks).text = artifact_list["cp"]
         else:
            ET.SubElement(subElement, "cp", type="file").text = artifact_list["cp"]


    def generate_flashing_config(self):
        self._root = ET.Element("conf")
        ET.SubElement(self._root, "cps").text = self.get_cps_exe_path()
        ET.SubElement(self._root, "cps_files_storage").text = self.get_cps_file_storage()
        self.ms_elements =  ET.SubElement(self._root, "FrodoSerial")

        if "PORT_APP_BRICK" in self._config["FLASHING"]:
            brick = ET.SubElement(self.ms_elements, "Brick")

            if "PORT_FLASH_BRICK" in self._config["FLASHING"]:
                ET.SubElement(brick, "port_app").text = self._config["FLASHING"]["PORT_APP_BRICK"]
                ET.SubElement(brick, "port").text = self._config["FLASHING"]["PORT_FLASH_BRICK"]
            else:
                ET.SubElement(brick, "port").text = self._config["FLASHING"]["PORT_APP_BRICK"]

            self.generate_common_field_in_config(brick, self.artifact_list)
        else:
            raise Exception("PORT_APP_BRICK is not found under FLASHING in the INI")
        if "PORT_APP_CH" in self._config["FLASHING"]:
            ch = ET.SubElement(self.ms_elements, "Head")
            ET.SubElement(ch, "port").text = self._config["FLASHING"]["PORT_APP_CH"]
            self.generate_common_field_in_config(ch, self.CH_artifact_list, self.Size, self.Blocks)
            ET.SubElement(ch, "kernel", type="pattern").text = self.CH_artifact_list["kernel"]
        self.dump_xml()

    def generate_cp(self, dest = None):
        #need to load kernel
        #ms_base.generate_cp(dest)
        status = 0
        brick_cp_location = os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION, self.artifact_list["cp"])
        ch_cp_location = os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION, self.CH_artifact_list["cp"])

        if not self.in_flash_mode and os.path.exists(brick_cp_location):
            target = os.path.join(self._flashing_path, self.artifact_list["cp"])
            if os.path.exists(target):
                os.remove(target)
            shutil.copy(brick_cp_location, target)
        else:
            dest = os.path.join(self._flashing_path, self.artifact_list["cp"])
            cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-r", self.brick_com, dest]
            print(cmd)
            status = subprocess.check_call(cmd)


        if status == 0:
            if not self.in_flash_mode and os.path.exists(ch_cp_location):
                target = os.path.join(self._flashing_path, self.CH_artifact_list["cp"])
                if os.path.exists(target):
                    os.remove(target)
                shutil.copy(brick_cp_location, target)
            else:
                self.set_blocks_and_size(self.flash_com)
                dest = os.path.join(self._flashing_path, self.CH_artifact_list["cp"])
                cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-r", self.flash_com, dest]
                print(cmd)
                status = subprocess.check_call(cmd)
                if status == 0:
                    cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-R", self.flash_com]
                    print(cmd)
                    subprocess.call(cmd)

    def preparing_cp(self):
        status = 0
        if not os.path.exists(os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION, self.artifact_list["cp"])):
            status = -1
            self.in_flash_mode = True
            if "PORT_APP_CH" in self._config["FLASHING"] and "PORT_APP_BRICK" in self._config["FLASHING"]:
                self.flash_com = self._config["FLASHING"]["PORT_APP_CH"]
                self.brick_com = self._config["FLASHING"]["PORT_APP_BRICK"]
                cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-f", self.flash_com]
                print("Entering flashing mode: %s"%" ".join(cmd))
                status = subprocess.check_call(cmd)
            else:
                raise Exception("PORT_APP_CH is not found under FLASHING in the INI")
            if status == 0:
                #load kernel
                kernel = find_all_files([self.CH_artifact_list['kernel']],self._flashing_path)[0][0]
                cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-K", self.flash_com, kernel]
                print(" ".join(cmd))
                status = subprocess.call(cmd)
                return status
        return status




class aragorn(ms_base):
    def __init__(self, config, flashing_path, artifact_path, encryption):
        super(aragorn,self).__init__(config, flashing_path, artifact_path)
        self.artifact_list["rpk"] = "\\d{4}(-\\d{2})?_NGP\\.rpk"
        self.artifact_list["flashstrap"] = "flashstrap\\-aragorn\\.s19"
        if config["FLASHING"]["IS_BOROMIR_TYPE"] == "TRUE":
            self.artifact_list["sw"] = "[BDIR]35%s.*_English\\.s19"%(encryption)
        else:
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

    def preparing_cp(self):
        self.cp_location = os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION, self.artifact_list["cp"])
        if not os.path.exists(self.cp_location ):
            return super(aragorn, self).preparing_cp()

    def generate_cp(self, dest = None):
        if os.path.exists(self.cp_location ):
            target = os.path.join(self._flashing_path, self.artifact_list["cp"])
            if os.path.exists(target):
                os.remove(target)
            shutil.copy(self.cp_location, target)
        else:
            return super(aragorn, self).generate_cp()

class barney(ms_base):
    def __init__(self, config, flashing_path, artifact_path, encryption):
        super(barney,self).__init__(config, flashing_path, artifact_path)
        self.artifact_list["rpk"] = "\\d{4}(-\\d{2})?_PTB\\.rpk"
        self.artifact_list["flashstrap"] = "FLASHSTRAP_13_.*\\.s19"
        self.artifact_list["sw"] = "[BDIR]13%s.*_english\\.s19"%(encryption)
        self.artifact_list["kernel"] = "ZPL03_KRNL_PATRIOT_.*\\.s19"
        self.artifact_list["loader"] = "ZPL03_SUBLOADER_.*\\.s19"
        self.in_flash_mode = False

    def generate_flashing_config(self):
        super(barney, self).generate_flashing_config()
        if "PORT_APP" in self._config["FLASHING"]:
            ET.SubElement(self.ms_elements, "port").text = self._config["FLASHING"]["PORT_APP"]
        else:
            raise Exception("PORT_APP is not found under FLASHING in the INI")
        ET.SubElement(self.ms_elements, "kernel", type="pattern").text =  self.artifact_list["kernel"]
        ET.SubElement(self.ms_elements, "loader", type="pattern").text =  self.artifact_list["loader"]
        self.dump_xml()

    def load_kernel(self):
        kernel = find_all_files([self.artifact_list["kernel"]], self._flashing_path)
        loader = find_all_files([self.artifact_list["loader"]], self._flashing_path)
        cmd = ["python",  os.path.join(self.get_tetra_flashing_dir(), "ucps.py"), "-K", str(self.flash_com),
               kernel[0][0], loader[0][0]]
        print(" ".join(cmd))
        subprocess.call(cmd)


    def preparing_cp(self):
        self.cp_location = os.path.join(os.getcwd(), self.DUMP_FILE_LOCATION, self.artifact_list["cp"])
        if not os.path.exists(self.cp_location ):
            return super(barney, self).preparing_cp()

    def generate_cp(self, dest = None):
        if os.path.exists(self.cp_location ):
            target = os.path.join(self._flashing_path, self.artifact_list["cp"])
            if os.path.exists(target):
                os.remove(target)
            shutil.copy(self.cp_location, target)
        else:
            self.load_kernel()
            return super(barney, self).generate_cp()


class flash_management(base):
    def __init__(self):
        super(flash_management,self).__init__()

    def prepare_artifacts(self):
        args = self.get_arg_value_by_opt("-i")
        args += self.get_arg_value_by_opt("--ignore")
        for config in self.get_config_list():
            ms_name = config.get('MS', 'Name')
            whitelisted = False
            for name in args:
                if str(ms_name).lower() == name.lower():
                    print("found white listing contains: %s, skipping %s"%(name, ms_name))
                    whitelisted = True
            if not whitelisted:
                self.configs.append(config)

        pool = Pool()
        pool.map(self.move_require_flashing_artifacts, self.configs)
        pool.close()
        pool.join()
        #for config in self.configs:
         #   ms_name = config.get('MS', 'Name')
          #  print(ms_name)
           # self.move_require_flashing_artifacts(config)

    def get_ms_id(self, ms_name):
        if ms_name.lower() == "frodo":
            return "27"
        elif ms_name.lower() == "aragorn":
            return "33"
        elif ms_name.lower() == "barney":
            return "13"
        else:
            raise Exception("Unrecgonized radio type: " + ms_name)

    def move_require_flashing_artifacts(self, config):
        ## create directory base on configs
        ms_name = config.get('MS', 'Name')
        ms_local_dir = os.path.join(self.LOCAL_BASE_LINE, ms_name)
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
            ms.copy_artifacts()
            ms.preparing_cp()
            ms.generate_cp()
            ms.generate_flashing_config()
            ms.begin_flash()



if __name__ == "__main__":
    flash_manager = flash_management()
    if not os.path.exists(flash_manager.CONFIGS_LOCATION):
        print("%s directory not found"%(flash_manager.CONFIGS_LOCATION))
        exit(1)
    flash_manager.set_arg_options(sys.argv[1:], 'i:', ['ignore='])

    if flash_manager.require_flash():
        print(" >>>> Begin flashing\n")
        flash_manager.prepare_artifacts()
    exit(0)
