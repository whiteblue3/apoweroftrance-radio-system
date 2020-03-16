import os
import time
import signal
from logger import Logger
from process import Process


class Master:
    def __init__(self, process_classes):
        self.__stop = False
        self.process = []
        self.logger = Logger('MasterProcess')

        self.process_classes = process_classes
        self.num_process = len(self.process_classes)

    def main(self):
        self.logger.log("MasterProcess", "Start Master, PID {0}".format(os.getpid()))

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        process_class_index = 0
        for process_id in range(self.num_process):
            pid = os.fork()
            process_class = self.process_classes[process_class_index]

            if pid == 0:
                process = Process()
                exit_code = process.main(process_class)
                exit(exit_code)
            else:
                self.logger.log("MasterProcess",
                                "Start {0} Process-{1} PID {2}".format(process_class.__name__, process_id, pid))
                self.process.append({"id": process_id, "pid": pid, "name": process_class.__name__})

            process_class_index += 1

        while not self.__stop:
            time.sleep(1)

        self.logger.log("MasterProcess", "Stop Master, PID {0}".format(os.getpid()))

    def stop(self, signum, frame):
        self.__stop = True
        self.logger.log("MasterProcess", "Receive Signal {0}".format(signum))

        for process in self.process:
            self.logger.log("MasterProcess",
                            "Send Signal {0} to {1} Process-{2} PID {3}".format(
                                signal.SIGTERM, process['name'], process['id'], process['pid']
                            ))
            os.kill(process['pid'], signal.SIGTERM)
