import os
# import json
from datetime import datetime
from dateutil.tz import tzlocal
from command import QUEUE, UNQUEUE, SETLIST, CMD
from process.shared import ns, cmd_queue
# from django_utils.db.db import DBControl
from logger import Logger


class MusicDaemon:
    name = None

    # # DB control
    # db = None

    def __init__(self, name):
        self.name = name
        self.__stop = False
        self.logger = Logger(MusicDaemon.__name__, name)

        ns_object = {"PLAYLIST": []}
        setattr(ns, name, ns_object)

        # db_username = os.environ.get('DB_USERNAME')
        # db_password = os.environ.get('DB_PASSWORD')
        # db_host = os.environ.get('DB_HOST')
        # db_port = os.environ.get('DB_PORT')
        # db_name = os.environ.get('DB_NAME')
        #
        # # Example of DBControl
        # self.db = DBControl(
        #     db_username,
        #     db_password,
        #     db_host,
        #     db_port,
        #     db_name
        # )
        # max_connections = self.query("select * from pg_settings where name='max_connections';")
        # self.logger.log("max_connections", max_connections)

    def __del__(self):
        pass

    # def query(self, sql):
    #     connection = self.db.connect()
    #     cursor = self.db.get_cursor(connection)
    #     self.db.query(cursor, sql)
    #     result = cursor.fetchall()
    #     cursor.close()
    #     self.db.close(connection)
    #     return result

    @property
    def PLAYLIST(self):
        ns_object = getattr(ns, self.name)
        return ns_object["PLAYLIST"]

    @PLAYLIST.setter
    def PLAYLIST(self, value):
        ns_object = getattr(ns, self.name)
        ns_object["PLAYLIST"] = value
        setattr(ns, self.name, ns_object)

    def now(self, tz=tzlocal()):
        return datetime.now(tz=tz).isoformat()

    def main(self,):
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

    def process_queue(self, cmd):
        try:
            location = cmd.data["location"]
        except KeyError as e:
            self.logger.log('error', str(e))
        else:
            try:
                artist = cmd.data["artist"]
            except KeyError as e:
                self.logger.log('error', str(e))
            else:
                try:
                    title = cmd.data["title"]
                except KeyError as e:
                    self.logger.log('error', str(e))
                else:
                    self.PLAYLIST.append(cmd.data)
                    self.logger.log('QUEUE', {"location": location, "artist": artist, "title": title})

    def process_unqueue(self, cmd):
        try:
            index_at = cmd.data["index_at"]
        except KeyError as e:
            self.logger.log('error', str(e))
        else:
            self.PLAYLIST.pop(index_at)
            self.logger.log('UNQUEUE', {"index_at": index_at})

    def process_setlist(self, cmd):
        is_no_error = False
        for queue in cmd.data:
            try:
                _ = queue["location"]
            except KeyError as e:
                self.logger.log('error', str(e))
            else:
                try:
                    _ = queue["artist"]
                except KeyError as e:
                    self.logger.log('error', str(e))
                else:
                    try:
                        _ = queue["title"]
                    except KeyError as e:
                        self.logger.log('error', str(e))
                    else:
                        is_no_error = True

        if is_no_error or len(cmd.data) == 0:
            self.PLAYLIST = cmd.data
            self.logger.log('SETLIST', self.PLAYLIST)

    def loop(self):
        if cmd_queue is not None and cmd_queue.empty() is False:
            cmd = cmd_queue.get()
            if self.name == cmd.target:
                # cmd_data = json.loads(cmd.data)
                self.logger.log('CMD RECV', cmd)

                if QUEUE == cmd.command:
                    self.process_queue(cmd)
                elif UNQUEUE == cmd.command:
                    self.process_unqueue(cmd)
                elif SETLIST == cmd.command:
                    self.process_setlist(cmd)
            else:
                cmd_queue.put(cmd)
