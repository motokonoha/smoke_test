#######################
We are using python 3 
#######################

A. For Generating HTML report 
-----------------------------
Please install the following python library :

1. konoha_HTMLTestRunner.py 
   - Copy it in one of the directories in your PYTHON_PATH directory
   - A recommended one : X:\Python34\Lib\site-packages
   - This contains modified code to support python 3.X  

2. mot-konoha-v1.0-unittest-xml-reporting-1.12.0 
   - Unzip and run : python setup.py install

B. Run the test
---------------------------------
1. Unzip the test scripts : Konoha_PrivatePythonEasiTest-v1.0.zip
  
   -modify the port and ISSI for ms1.ini | ms2.ini | ms3.ini in       
    \Konoha_PrivatePythonEasiTest-v1.0\cfgs
   -make sure your radio settings are according to the normal testing settings 
    (i configure my radio manually)
   - main file to call for testing :  konoha_main_test_azu.py

Note : the script does not load any cpv to your radios. it just run the test. Please make sure the radios has the needed settings  (talkgroup etc)

To run the test :  
+++++++++++++++++

  * To run default test case (set to only "ms1_groupcall test" for now) 
  python3 -u  konoha_main_test_azu.py -j test-results.xml -o 020 
  
  * To run specific test case :
  python3 -u  konoha_main_test_azu.py -j test-results.xml -o 020 -testname GroupCalls.ms2_GroupCalls.test_001_ms1_enters_TXI_mode

  * To run a group of test cases : 
   python3 -u konoha_main_test_azu.py -j test-results.xml -o 020 -testname GroupCalls.ms2_GroupCalls

C. Generated HTML and XML
-------------------
It will in the same folder as the test cases you have unzipped previously. 
Current generated html file name : BDBOS_report.html

---------------
X. TODO list
---------------
1. how to load the CPV too (i think CM is taking care of this , )
2. Flexibility to change the name/folder of generated html to include time in order not to override. 
3. Generate HTML from xml generated [Working on this , azura ]
4. Generate the test-list.xml from a local website with tick cases (like jenkins. have to see the artifacts of any completed private test to see the XML structure) 

etc


-azura
