import multiprocessing
from multiprocessing import Queue

# CMD Queue
cmd_queue = Queue()

manager = multiprocessing.Manager()
ns = manager.Namespace()
