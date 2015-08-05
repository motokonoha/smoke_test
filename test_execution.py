
from flash_cpv import *
from whitelist_execution import *
import subprocess

class test_execution(base):
    def __init__(self):
       super(test_execution, self).__init__()

    def flash_cpv(self):
        suite1 = unittest.TestLoader().loadTestsFromTestCase(flash_cpv)
        suite = unittest.TestSuite([suite1])
        unittest.TextTestRunner(verbosity=2).run(suite)

    def execute_test(self):
        try:
            subprocess.check_call(['python', 'verification.py'])
            subprocess.check_call(['python', 'whitelist_execution.py'])
        except:
            exit(-1)

if __name__ == "__main__":
    test_executor = test_execution()
    #test_executor.flash_cpv()
    test_executor.execute_test()



