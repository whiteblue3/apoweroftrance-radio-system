import os
from utils.db.db import DBControl

from logger import Logger


class MusicDaemon:
    PLAYLIST = []
    is_publishing = False

    def __init__(self):
        self.__stop = False
        self.is_publishing = False
        self.logger = Logger('MusicDaemon')

        # Example of DBControl
        control = DBControl('whiteblue3', '', '127.0.0.1', 5432, 'radio')
        connection = control.connect()
        cursor = control.get_cursor(connection)
        control.query(cursor, "select * from pg_settings where name='max_connections';")
        max_connections = cursor.fetchall()
        self.logger.log("max_connections", max_connections)
        cursor.close()
        control.close(connection)

    def main(self):
        self.logger.log('start', {
            'pid': os.getpid()
        })
        while not self.__stop:
            self.loop()

        self.logger.log('stop', {
            'pid': os.getpid()
        })
        return 0

    def stop(self):
        self.__stop = True

    def loop(self):
        # self.logger.log('sing', {
        #     'song': song
        # })
        pass
