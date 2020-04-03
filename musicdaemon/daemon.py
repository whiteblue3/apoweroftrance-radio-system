import os
# import json
from datetime import datetime
from dateutil.tz import tzlocal
from commands import QUEUE, UNQUEUE, SETLIST, CMD
from process.shared import ns, cmd_queue, get_ns_obj, set_ns_obj
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

        ns_object = {
            "now_playing": {
                "artist": None,
                "title": None,
                "location": None
            },
            "playlist": []
        }
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
    def now_playing(self):
        return get_ns_obj(self.name, "now_playing")

    @now_playing.setter
    def now_playing(self, value):
        set_ns_obj(self.name, "now_playing", value)

    @property
    def playlist(self):
        return get_ns_obj(self.name, "playlist")

    @playlist.setter
    def playlist(self, value):
        set_ns_obj(self.name, "playlist", value)

    def now(self, tz=tzlocal()):
        return datetime.now(tz=tz).isoformat()

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
                    self.playlist.append(cmd.data)
                    self.logger.log('QUEUE', {"location": location, "artist": artist, "title": title})

    def process_unqueue(self, cmd):
        try:
            index_at = cmd.data["index_at"]
        except KeyError as e:
            self.logger.log('error', str(e))
        else:
            self.playlist.pop(index_at)
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
            self.playlist = cmd.data
            self.logger.log('SETLIST', self.playlist)

    def loop(self):
        if cmd_queue is not None and cmd_queue.empty() is False:
            # Dequeue from queue (pop)
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
                # If else, rollback to queue
                cmd_queue.put(cmd)
