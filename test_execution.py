
from flash_cpv import *
from base import *
import subprocess
import os
import re
import unittest
import argparse

class test_execution(base):
    def __init__(self):
        super(test_execution, self).__init__()


    def flash_cpv(self):
        suite1 = unittest.TestLoader().loadTestsFromTestCase(flash_cpv)
        suite = unittest.TestSuite([suite1])
        unittest.TextTestRunner(verbosity=2).run(suite)

    def execute_test(self):
        try:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            subprocess.check_call(['python', os.path.join(script_dir, "verification.py")])
        except:
            exit(-1)


if __name__ == "__main__":
    test = test_execution()
    if not os.path.exists(os.path.join(os.getcwd(),"temp")):
        os.mkdir(os.path.join(os.getcwd(),"temp"))
    startTime = datetime.now()
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", help="type in '--html=true' to generate a HTML report", type = str)
    parser.add_argument("--whitelist", help ="type in '--whitelist=Filename.Classname.Function' to run tests", type = str)
    parser.add_argument("--cpv", help="type in '--cpv=true' to flash the CP", type =str)
    parser.add_argument('--process', nargs=argparse.REMAINDER)
    parser.add_argument('--run', nargs=argparse.REMAINDER)
    parser.add_argument('--ignore', nargs=argparse.REMAINDER)
    arguments = parser.parse_args()
    if arguments.cpv=="true":
        test.flash_cpv()

    suite = unittest.TestSuite()
    suite_run = unittest.TextTestRunner()
    have_whitelist = test.is_whitelist_available()
    #if user pass whitelist argument
    if arguments.whitelist!= None :
        whitelist = test.argument_unittest_list(arguments.whitelist)
        suite.addTests(whitelist)
        if arguments.html=="true":
            test.create_html_report(suite)
        else:
            suite_run.run(suite)
            test.get_time_elapsed(startTime)
    #if user pass whitelist into json
    elif have_whitelist:
        test.execute_test()
        json_list = []
        json_list = test.create_whitelist()
        suite.addTests(json_list)
        if arguments.html == "true":
            test.create_html_report(suite)
        else:
            suite_run.run(suite)
            test.get_time_elapsed(startTime)
    #not whitelist found in both json and argument
    elif not have_whitelist:
        tests_list = []
        filepath = os.path.join(os.getcwd(), "test_scripts")
        for file in os.listdir(filepath):
                if file.endswith(".py"):
                    filename = []
                    filename = re.split('.py',file)
                    tests_list.append(filename[0])
        print(tests_list)
        whitelist = test.generate_unittest_list(tests_list)
        suite.addTests(whitelist)
        if arguments.html =="true":
            test.create_html_report(suite)
        else:
            suite_run.run(suite)
            test.get_time_elapsed(startTime)

















