

from base import *
from multiprocessing import *

class verification(base):

    def semaphore_join(self, processes, number_of_allowed_thread = 5):
         if len(processes) > number_of_allowed_thread:
                while(len(processes) > 0):
                    process = processes.pop()
                    process.join()

    def process_queue_verification(self, processes, process_queue):
        result = []
        while(not process_queue.empty()):
            result.append(process_queue.get(timeout =1))
        #for _ in processes:
        for status in result:
            if status == False:
                exit(-1)


    def validation(self,script_path):
        q = Queue()
        processes =[]
        for (file_name) in self.get_filename():
            p = Process(target=self.verify_filename, args=(file_name,q, script_path))
            p.start()
            processes.append(p)
            self.semaphore_join(processes)
        # if number of process less than 5 then we need to wait until everything is ok
        self.semaphore_join(processes, 0)
        self.process_queue_verification(processes,q)
        processes = []
        for (file_name, class_name) in self.get_class():
             p = Process(target=self.verify_class, args=(file_name,class_name, q,script_path))
             p.start()
             processes.append(p)
             self.semaphore_join(processes)
        # if number of process less than 5 then we need to wait until everything is ok
        self.semaphore_join(processes, 0)
        self.process_queue_verification(processes,q)

        processes = []
        for (file_name,class_name,function_name) in self.get_function():
            p = Process(target=self.verify_function, args=(file_name,class_name,function_name, q,script_path))
            p.start()
            processes.append(p)
            self.semaphore_join(processes)
        # if number of process less than 5 then we need to wait until everything is ok
        self.semaphore_join(processes, 0)
        self.process_queue_verification(processes,q)




