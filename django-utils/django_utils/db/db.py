"""
데이터베이스 연결 헬퍼
"""
from psycopg2.extras import RealDictCursor
from . import dbpool
from logger import Logger


# max_connections : select * from pg_settings where name='max_connections';
class DBControl:
    dsn = None
    pool = None
    logger = None

    def __init__(self, user, password, host, port, dbname):
        self.logger = Logger(DBControl.__name__, "db")
        self.dsn = "postgresql://%s:%s@%s:%s/%s" % (user, password, host, port, dbname)
        self.pool = dbpool.ProcessSafePoolManager(1, 198, dsn=self.dsn)

    # def __init__(self, dsn):
    #     self.dsn = dsn
    #     self.pool = dbpool.ProcessSafePoolManager(1, 198, dsn=self.dsn)

    def connect(self):
        return self.pool.getconn()

    def get_cursor(self, connection):
        return connection.cursor(cursor_factory=RealDictCursor)

    def query(self, cursor, sql, parameter=None):
        try:
            cursor.execute(sql, parameter)
        except Exception as e:
            self.logger.log("error", "Database Query Error {}".format(e))
            raise

    def close(self, connection):
        try:
            self.pool.putconn(connection)
        except Exception as e:
            self.logger.log("error", "Database Close Error {}".format(e))
            raise
