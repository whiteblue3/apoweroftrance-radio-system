import os
# import json
from datetime import datetime
from dateutil.tz import tzlocal
from commands import QUEUE, UNQUEUE, SETLIST, CMD
from process.shared import ns, cmd_queue, get_ns_obj, set_ns_obj, ns_config
from logger import Logger


class MusicDaemon:
    name = None
    icecast2_config = None

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

        try:
            self.icecast2_config = ns_config.icecast2[name]
        except KeyError:
            pass

        self.logger.log("icecast2_config", self.icecast2_config)

    def __del__(self):
        pass

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
