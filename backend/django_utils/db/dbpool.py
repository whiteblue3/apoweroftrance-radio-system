"""
데이터베이스 커넥션 풀
"""
import os
from psycopg2.pool import ThreadedConnectionPool


class ProcessSafePoolManager:

    def __init__(self, *args, **kwargs):
        self.last_seen_process_id = os.getpid()
        self.args = args
        self.kwargs = kwargs
        self._init()

    def _init(self):
        self._pool = ThreadedConnectionPool(*self.args, **self.kwargs)

    def getconn(self):
        current_pid = os.getpid()
        if not (current_pid == self.last_seen_process_id):
            self._init()
            print("New id is %s, old id was %s" % (current_pid, self.last_seen_process_id))
            self.last_seen_process_id = current_pid
        return self._pool.getconn()

    def putconn(self, conn):
        return self._pool.putconn(conn)

