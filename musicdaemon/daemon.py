import os
import json
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzlocal
from command import QUEUE, UNQUEUE
from utils.db.db import DBControl
from logger import Logger


class MusicDaemon:
    name = None
    PLAYLIST = []
    is_publishing = False

    # DB control
    db = None

    def __init__(self, name):
        self.name = name
        self.__stop = False
        self.is_publishing = False
        self.logger = Logger(MusicDaemon.__name__, name)

        db_username = os.environ.get('DB_USERNAME')
        db_password = os.environ.get('DB_PASSWORD')
        db_host = os.environ.get('DB_HOST')
        db_port = os.environ.get('DB_PORT')
        db_name = os.environ.get('DB_NAME')

        # Example of DBControl
        self.db = DBControl(
            db_username,
            db_password,
            db_host,
            db_port,
            db_name
        )
        max_connections = self.query("select * from pg_settings where name='max_connections';")
        self.logger.log("max_connections", max_connections)

    def __del__(self):
        pass

    def query(self, sql):
        connection = self.db.connect()
        cursor = self.db.get_cursor(connection)
        self.db.query(cursor, sql)
        result = cursor.fetchall()
        cursor.close()
        self.db.close(connection)
        return result

    def now(self, tz=tzlocal()):
        return datetime.now(tz=tz).isoformat()

    def main(self, cmd_queue=None):
        self.logger.log('start', {
            'pid': os.getpid()
        })

        while not self.__stop:
            self.loop(cmd_queue)

        self.logger.log('stop', {
            'pid': os.getpid()
        })
        return 0

    def stop(self):
        self.__stop = True

    def process_queue(self, cmd):
        try:
            track_id = cmd.data["track_id"]
        except KeyError as e:
            self.logger.log('error', str(e))
        else:
            try:
                queue_at = cmd.data["queue_at"]
            except KeyError:
                queue_at = None

            if queue_at is not None:
                try:
                    parse(queue_at, fuzzy=False)
                except ValueError as e:
                    self.logger.log('error', str(e))

            self.logger.log('QUEUE', {"track_id": track_id, "queue_at": queue_at})

    def process_unqueue(self, cmd):
        try:
            queue_id = cmd.data["queue_id"]
        except KeyError as e:
            self.logger.log('error', str(e))
        else:
            self.logger.log('UNQUEUE', {"queue_id": queue_id})

    def loop(self, cmd_queue):
        # self.logger.log('sing', {
        #     'song': song
        # })
        if cmd_queue is not None and cmd_queue.empty() is False:
            cmd = cmd_queue.get()
            if self.name in cmd.target:
                # cmd_data = json.loads(cmd.data)
                self.logger.log('CMD RECV', cmd)

                if QUEUE == cmd.command:
                    self.process_queue(cmd)
                elif UNQUEUE == cmd.command:
                    self.process_unqueue(cmd)
