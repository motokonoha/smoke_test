from base import *
import subprocess
import os
import re
import unittest
import argparse
import pprint
from verification import *
from mot_test import get_tests_from_xml, get_tests_from_list
copied_script_path =[]

class test_execution(base):
    def __init__(self):
        super(test_execution, self).__init__()

    def flash_cpv(self):
        suites = unittest.TestSuite()
        suites.addTests(unittest.TestLoader().loadTestsFromName("flash_cpv.flash_cpv"))
        unittest.TextTestRunner(verbosity=2).run(suites)

    def my_import(self, name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return

    def run_test(self,test_list):
        original = os.getcwd()
        for script_path in copied_script_path:
            suites = unittest.TestSuite()
            print ("\n" +script_path)
            os.chdir(script_path)
            added_test_list = []
            for test in test_list:
                filename = test.split('.')[0]
                if os.path.exists("%s.py"%(filename)):
                    try:
                        suites.addTests(unittest.TestLoader().loadTestsFromName(test))
                        print("ADDED: %s"%test)
                        added_test_list.append(test)
                    except Exception as e:
                        print("FAILED: %s"%test)
                        print("\tException: %s"%e)
            for added_test in added_test_list:
                test_list.remove(added_test)
            try:
                self.run_generate_report(arguments, suites ,test)
            except Exception as e:
                print(e)
                exit(-1)
        os.chdir(original)

    def prerun_test(self, pretests):
        pretest_list = pretests.split(',')
        self.run_test(pretest_list)
        if len(pretest_list) > 0:
           print("ERROR: Following pre run test fail to run \n %s"%('\n'.join(pretest_list)))
           exit(-1)


    def execute_test(self,script_path):
        print (script_path)
        try:
            print("Verify run_test")
            run_test = verification()
            print("Run_test start validation")
            run_test.validation(script_path)
            print ("Verification PASSED")
        except Exception as e:
            pprint.pprint (e)
            print ("Verification FAILED")
            exit(-1)

    def run_generate_report(self, arguments, suites, test ):
        if arguments.xml and arguments.xml != "":
            self.create_xml_report(suites, arguments.xml)
        elif arguments.html and arguments.html != "":
            self.create_html_report(suites, arguments.html, test)
        else:
            unittest.TextTestRunner().run(suites)
            self.get_time_elapsed(startTime)


if __name__ == "__main__":
    test = test_execution()
    file_path = os.path.join(os.getcwd(),"temp")
    if os.path.exists(file_path):
        shutil.rmtree(file_path)
    os.mkdir(file_path)
    startTime = datetime.now()
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", help="type in '--html=<desire file path>' to generate a HTML report", type = str)
    parser.add_argument("--xml", help="type in '--xml=<desire file path>' to generate a XML report", type = str)
    parser.add_argument("--whitelist", help ="type in '--whitelist=Filename.Classname.Function' to run tests", type = str)
    parser.add_argument("--rerun", help ="type in '--rerun=xml path' to rerun tests", type = str)
    parser.add_argument("--cpv", help="type in '--cpv' to flash the CP", action ="store_true")
    parser.add_argument("--file_path",help="type in '--file_path=test_scripts_path' or '--file_path="" if gather test is run",type=str)
    parser.add_argument("--cfgs", help="directory where python *.ini files are stored", type = str)
    parser.add_argument("--logs", help="directory where python logs files are stored", type=str)
    parser.add_argument("--prerun", help="test script that need to run before any of the test.", type=str)
    parser.add_argument('--process', nargs=argparse.REMAINDER)
    parser.add_argument('--run', nargs=argparse.REMAINDER)
    parser.add_argument('--ignore', nargs=argparse.REMAINDER)
    arguments = parser.parse_args()

    if arguments.cfgs and os.path.exists(arguments.cfgs):
        os.environ["PYEASITEST_CFGS"] = arguments.cfgs
    if arguments.logs:
        os.environ["PYEASITEST_LOGS"] = arguments.logs
    else:
        arguments.logs = "logs/"

    if arguments.file_path == None:
        test.sync_test()
        for script_path in test.copy_test_script():
            copied_script_path.append(script_path)
    else:
        test_path = arguments.file_path.split(",")
        for script_path in test_path:
            if(os.path.exists(script_path)):
                copied_script_path.append(script_path)
            else:
                print ("ERROR: %s is not found \n Please type in the correct file path"%(script_path))
                exit(-1)

    for script_path in copied_script_path:
        sys.path.append(script_path)

    if arguments.prerun:
        print("pre run tests \n%s"%("\n".join(arguments.prerun.split(','))))
        test.prerun_test(arguments.prerun)

    if arguments.cpv:
        print("cpv created according to json: %s"%arguments.cpv)
        test.flash_cpv()

    suites = unittest.TestSuite()
    suite_run = unittest.TextTestRunner()
    have_whitelist = test.is_whitelist_available()

    #re-run file will enter here
    if arguments.rerun != None:
        print("rerun: "+arguments.rerun)
        if os.path.exists(arguments.rerun):
            suites = get_tests_from_xml(arguments.rerun)
            test.run_generate_report(arguments, suites , test)
        else:
            print ("%s is not found"%arguments.rerun)
            exit(-1)

    #if user pass whitelist argument
    elif arguments.whitelist != None :
        arg_list = test.argument_unittest_list(arguments.whitelist)
        test.run_test(arg_list)

    #if user pass whitelist into json
    elif have_whitelist:
        for script_path in copied_script_path:
            test.execute_test(script_path)
            json_list = test.create_whitelist(script_path)
            test.run_test(json_list)

    #not whitelist found in both json and argument
    elif not have_whitelist:
        test_list = []
        for script_path in copied_script_path:
            for file in os.listdir(script_path):
                if file.endswith(".py"):
                    filename = []
                    filename = re.split('.py',file)
                    test_list.append(filename[0])
        test.run_test(test_list)

    print(arguments.logs +" => logs.zip")
    if not os.path.exists("out"):
        os.mkdir("out")
    test.zipper(arguments.logs, "out/logs.zip")

















