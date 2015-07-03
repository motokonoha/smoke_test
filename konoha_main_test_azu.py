#author Ooi Song Qiang (prg684)
#edited by Azura
import argparse, os, shutil, zipfile
import unittest, xmlrunner
import xml.dom
import HTMLTestRunner
from xml.dom.minidom import parse
from SDS import ms1_SDS, ms2_SDS, ms3_SDS
from TPCTestsOneMs import TPCTests
from TPCTestsTwoMS import TPCTestsTwoMs
from Attachments import ms2_Attachments, ms1_Attachments, ms3_Attachments
from FDPC import ms2_FDPC, ms1_FDPC, ms3_FDPC
from HDPC import ms2_HDPC, ms1_HDPC, ms3_HDPC
from PD import ms1_SSPD, ms2_SSPD, ms3_SSPD, ms1_MSPD, ms2_MSPD, ms3_MSPD, ms1_QAM
from GroupCalls import ms2_GroupCalls, ms1_GroupCalls, ms3_GroupCalls
from SetupCP import setup_cp
from checklist import ms1_Checklist
from checklist import ms2_Checklist, ms3_Checklist
from TPC import ms1_TPC
from DMO import ms1_DMO, ms1_DMO2A, ms1_DMO2B, ms1_DMO2C, ms2_DMO, ms2_DMO2A, ms2_DMO2B, ms2_DMO2C, ms3_DMO, ms3_DMO2A, ms3_DMO2B, ms3_DMO2C
from Gateway import ms1_Gateway, ms1_Gateway_2A, ms1_Gateway_2B, ms1_Gateway_2C
from CleanUp import clean_up
from EmerAlert import ms1_EmerAlert, ms2_EmerAlert
from Repeater import ms1_Repeater, ms1_Repeater_2C, ms2_Repeater, ms2_Repeater_2C, ms3_Repeater, ms3_Repeater_2C
from Repeater_interactive import ms1_Repeater_interactive, ms1_Repeater_interactive_2C, ms2_Repeater_interactive, ms2_Repeater_interactive_2C, ms3_Repeater_interactive, ms3_Repeater_interactive_2C
import re
from mot_test import get_tests_from_xml

def print_mobiles_versions(junit_name, outsuffix):
    base, ext = os.path.splitext(junit_name)
    filename = base+"-"+outsuffix+ext
    ms1 = ""
    ms2 = ""
    ms3 = ""
    with open(filename) as f:
        txt = f.read()
        m = re.search(r'ms1\:\sRadio\sVersion\:\s(.*?)\s', txt, re.M|re.I)
        if m:
            ms1 = m.group(1)
        m = re.search(r'ms2\:\sRadio\sVersion\:\s(.*?)\s', txt, re.M|re.I)
        if m:
            ms2 = m.group(1)
        m = re.search(r'ms3\:\sRadio\sVersion\:\s(.*?)\s', txt, re.M|re.I)
        if m:
            ms3 = m.group(1)
    print("MS versions: ms1="+ms1+" ms2="+ms2+" ms3="+ms3)

def zipper(dir, zip_file):
    zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
    root_len = len(os.path.abspath(dir))
    for root, dirs, files in os.walk(dir):
        archive_root = os.path.abspath(root)[root_len:]
        for f in files:
            fullpath = os.path.join(root, f)
            archive_name = os.path.join(archive_root, f)
            zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
    zip.close()
    return zip_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()         
    parser.add_argument("-f","--filepath", help="path to the xml file with testcases", type=str)
    parser.add_argument("-j","--junit", help="name of the file with junit results", type=str)
    parser.add_argument("-o","--outsuffix", help="suffix to name of the file with junit results", type=str)
    parser.add_argument("--cfgs", help="directory where python *.ini files are stored", type=str)
    parser.add_argument("--logs", help="directory where python logs files are stored", type=str)
    parser.add_argument("--verbosity", help="verbosity level", type=int)
    parser.add_argument("-t","--testname", help="full name of 1 test/test_suite to be executed e.g. GroupCalls.ms2_GroupCalls.test_001_ms1_enters_TXI_mode or GroupCalls.ms2_GroupCalls", type=str)
    arguments = parser.parse_args()

    fp = open('BDBOS_report.html', 'wb')
    htmlrunner = HTMLTestRunner.HTMLTestRunner(
                stream=fp,
                title='BDBOS test station result',
                description='This test is conducted on level 7 for BDBOS test cases set based on Jenkins'
                )

    if arguments.verbosity:
        verbosity_level = arguments.verbosity
    else:
        verbosity_level = 2

    if arguments.cfgs and os.path.exists(arguments.cfgs):
        os.environ["PYEASITEST_CFGS"] = arguments.cfgs
    if arguments.logs:
        os.environ["PYEASITEST_LOGS"] = arguments.logs
    if arguments.junit:
        junit_name = arguments.junit
    else:
        junit_name = "test-results.xml"
    if arguments.outsuffix:
        outsuffix = arguments.outsuffix
    else:
        outsuffix = "tmp"

    # common test cases
    suite999 = unittest.TestLoader().loadTestsFromTestCase(clean_up)
    suite0 = unittest.TestLoader().loadTestsFromTestCase(setup_cp)

    if (arguments.filepath == None and arguments.testname == None):

        #suite1 = unittest.TestLoader().loadTestsFromTestCase(TPCTests)
        suite2 = unittest.TestLoader().loadTestsFromTestCase(ms1_SDS)
        suite3 = unittest.TestLoader().loadTestsFromTestCase(ms2_SDS)
        #suite4 = unittest.TestLoader().loadTestsFromTestCase(TPCTestsTwoMs)
        suite4 = unittest.TestLoader().loadTestsFromTestCase(ms2_GroupCalls)
        suite5 = unittest.TestLoader().loadTestsFromTestCase(ms1_GroupCalls)
        suite6 = unittest.TestLoader().loadTestsFromTestCase(ms2_Attachments)
        suite7 = unittest.TestLoader().loadTestsFromTestCase(ms1_Attachments)

        suite8 = unittest.TestLoader().loadTestsFromTestCase(ms2_FDPC)
        suite9 = unittest.TestLoader().loadTestsFromTestCase(ms1_FDPC)
        suite10 = unittest.TestLoader().loadTestsFromTestCase(ms2_HDPC)
        suite11 = unittest.TestLoader().loadTestsFromTestCase(ms1_HDPC)
        suite12 = unittest.TestLoader().loadTestsFromTestCase(ms1_SSPD)
        suite13 = unittest.TestLoader().loadTestsFromTestCase(ms2_SSPD)
        suite14 = unittest.TestLoader().loadTestsFromTestCase(ms3_SSPD)
        suite15 = unittest.TestLoader().loadTestsFromTestCase(ms1_MSPD)
        suite16 = unittest.TestLoader().loadTestsFromTestCase(ms2_MSPD)
        suite17 = unittest.TestLoader().loadTestsFromTestCase(ms3_MSPD)
        suite18 = unittest.TestLoader().loadTestsFromTestCase(ms1_QAM)
        suite19 = unittest.TestLoader().loadTestsFromTestCase(ms1_Checklist)
        suite20 = unittest.TestLoader().loadTestsFromTestCase(ms2_Checklist)
        suite21 = unittest.TestLoader().loadTestsFromTestCase(ms1_TPC)

        suite22 = unittest.TestLoader().loadTestsFromTestCase(ms1_DMO)
        suite23 = unittest.TestLoader().loadTestsFromTestCase(ms1_DMO2A)
        suite24 = unittest.TestLoader().loadTestsFromTestCase(ms1_DMO2B)
        suite25 = unittest.TestLoader().loadTestsFromTestCase(ms1_DMO2C)
        suite26 = unittest.TestLoader().loadTestsFromTestCase(ms2_DMO)
        suite27 = unittest.TestLoader().loadTestsFromTestCase(ms2_DMO2A)
        suite28 = unittest.TestLoader().loadTestsFromTestCase(ms2_DMO2B)
        suite29 = unittest.TestLoader().loadTestsFromTestCase(ms2_DMO2C)
        suite30 = unittest.TestLoader().loadTestsFromTestCase(ms3_DMO)
        suite31 = unittest.TestLoader().loadTestsFromTestCase(ms3_DMO2A)
        suite32 = unittest.TestLoader().loadTestsFromTestCase(ms3_DMO2B)
        suite33 = unittest.TestLoader().loadTestsFromTestCase(ms3_DMO2C)
        suite34 = unittest.TestLoader().loadTestsFromTestCase(ms1_Gateway)
        suite35 = unittest.TestLoader().loadTestsFromTestCase(ms1_Gateway_2A)
        suite36 = unittest.TestLoader().loadTestsFromTestCase(ms1_Gateway_2B)
        suite37 = unittest.TestLoader().loadTestsFromTestCase(ms1_Gateway_2C)
        suite38 = unittest.TestLoader().loadTestsFromTestCase(ms1_Repeater)
        suite42 = unittest.TestLoader().loadTestsFromTestCase(ms1_Repeater_2C)
        suite39 = unittest.TestLoader().loadTestsFromTestCase(ms1_Repeater_interactive)
        suite43 = unittest.TestLoader().loadTestsFromTestCase(ms1_Repeater_interactive_2C)
        suite40 = unittest.TestLoader().loadTestsFromTestCase(ms1_EmerAlert)
        suite41 = unittest.TestLoader().loadTestsFromTestCase(ms2_EmerAlert)

        suite44= unittest.TestLoader().loadTestsFromTestCase(ms3_Attachments)
        suite45= unittest.TestLoader().loadTestsFromTestCase(ms3_FDPC)
        suite46 = unittest.TestLoader().loadTestsFromTestCase(ms3_GroupCalls)
        suite47 = unittest.TestLoader().loadTestsFromTestCase(ms3_HDPC)
        suite48 = unittest.TestLoader().loadTestsFromTestCase(ms2_Repeater)
        suite49 = unittest.TestLoader().loadTestsFromTestCase(ms2_Repeater_2C)
        suite50 = unittest.TestLoader().loadTestsFromTestCase(ms3_Repeater)
        suite51 = unittest.TestLoader().loadTestsFromTestCase(ms3_Repeater_2C)
        suite52 = unittest.TestLoader().loadTestsFromTestCase(ms3_SDS)
        suite53 = unittest.TestLoader().loadTestsFromTestCase(ms3_Checklist)
        suite54 = unittest.TestLoader().loadTestsFromTestCase(ms2_Repeater_interactive)
        suite55 = unittest.TestLoader().loadTestsFromTestCase(ms2_Repeater_interactive_2C)
        suite56 = unittest.TestLoader().loadTestsFromTestCase(ms3_Repeater_interactive)
        suite57 = unittest.TestLoader().loadTestsFromTestCase(ms3_Repeater_interactive_2C)

        
        #suite = unittest.TestSuite([suite22, suite23, suite24, suite25, suite26, suite27, suite28, suite29, suite30, suite31, suite32, suite33, suite999])
        #suite = unittest.TestSuite([suite22, suite23, suite26, suite27, suite30, suite31, suite999])
        #suite = unittest.TestSuite([suite22, suite26, suite30, suite999])
        suite = unittest.TestSuite([suite4, suite999])

        #suite = unittest.TestSuite([suite13, suite14, suite15])
        #suite = unittest.TestSuite([suite0, suite4, suite5, suite6, suite7, suite8, suite9, suite10, suite11, suite19, suite20, suite22, suite23, suite24, suite25, suite26, suite27, suite28, suite29, suite30, suite31, suite31, suite32, suite33, suite34, suite35, suite999])
        #tutaj bez packet data
        #suite = unittest.TestSuite([suite0, suite2, suite3, suite4, suite5, suite6, suite7, suite8 ,suite9, suite10, suite11, suite19, suite20, suite21, suite22, suite23, suite24, suite25, suite26, suite27, suite28, suite29, suite30, suite31, suite32, suite33])

    elif arguments.testname != None:

        ### Azura's testing
        ###
        #test_to_run = unittest.TestLoader().discover(start_dir='.',pattern='GroupCalls.py'  )
        #print ("TestCaseNames: ", unittest.TestLoader().getTestCaseNames(ms2_GroupCalls))
        #suite = unittest.TestLoader().loadTestsFromName("GroupCalls.ms2_GroupCalls.test_001_ms1_enters_TXI_mode")
        #suite = unittest.TestLoader().loadTestsFromName("GroupCalls.ms2_GroupCalls")
        print (arguments.testname)

        suite_2_test = unittest.TestLoader().loadTestsFromName(arguments.testname )
        suite = unittest.TestSuite([suite_2_test, suite999])
    else:
        suite = get_tests_from_xml(arguments.filepath)
        #suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromNames(testModules))

    #result = xmlrunner.XMLTestRunner(verbosity=2, per_test_output=True, output=junit_name, outsuffix=outsuffix).run(suite)

    result = xmlrunner.XMLTestRunner(verbosity=verbosity_level, output=junit_name, outsuffix=outsuffix ).run(suite)
    #runner.run(suite)
    htmlrunner.generateReport(suite, result)

    #print_mobiles_versions(junit_name, outsuffix)
    #zipper("logs/", "logs.zip")
