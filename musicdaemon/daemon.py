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

        db_username = os.environ.get('DB_USERNAME')
        db_password = os.environ.get('DB_PASSWORD')
        db_host = os.environ.get('DB_HOST')
        db_port = os.environ.get('DB_PORT')
        db_name = os.environ.get('DB_NAME')

        # Example of DBControl
        control = DBControl(
            db_username,
            db_password,
            db_host,
            db_port,
            db_name
        )
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
