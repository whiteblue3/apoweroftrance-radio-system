import os
# import shouty
import shout
# import json
from datetime import datetime
from dateutil.tz import tzlocal
from commands import QUEUE, UNQUEUE, SETLIST, CMD
from process.shared import ns, cmd_queue, get_ns_obj, set_ns_obj, ns_config
from logger import Logger


class MusicDaemon:
    name = None
    icecast2_config = None

    # Local playlist
    PLAYLIST = []

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

    # playlist for ns
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

        s = shout.Shout()

        s.host = self.icecast2_config["host"]
        s.port = int(self.icecast2_config["port"])
        s.user = self.icecast2_config["user"]
        s.password = self.icecast2_config["password"]
        s.mount = '/' + self.icecast2_config["mount"]
        s.format = self.icecast2_config["codec"]
        s.protocol = 'http'
        s.name = self.icecast2_config["name"]
        s.genre = self.icecast2_config["genre"]
        # s.url = ''
        s.public = 1    # 0 | 1
        s.audio_info = {
            shout.SHOUT_AI_BITRATE: '128000',
            shout.SHOUT_AI_SAMPLERATE: '44100'
        }

        is_connected = True
        try:
            s.open()
        except shout.ShoutException as e:
            is_connected = False
            self.logger.log('icecast2', "{}".format(e))
        else:
            self.logger.log('icecast2', "connected")
            # TODO: 데몬 시작 콜백

        is_streaming = False
        f = None

        while not self.__stop:
            self.loop()

            if is_connected is True:
                if is_streaming is False:
                    if len(self.PLAYLIST) > 0:
                        try:
                            self.now_playing = self.PLAYLIST.pop()
                            self.playlist = self.PLAYLIST

                            filename = str(self.now_playing["location"])
                            s.set_metadata({'song': "{0} - {1}".format(self.now_playing["artist"], self.now_playing["title"])})

                            # TODO: 재생 시작 콜백

                            f = open(filename, 'rb')
                        except IndexError:
                            continue
                        else:
                            is_streaming = True
                else:
                    chunk = f.read(4096)
                    if not chunk:
                        is_streaming = False
                        f.close()
                        self.now_playing = None

                        # TODO: 재생 종료 콜백
                    else:
                        s.send(chunk)
                        s.sync()

        s.close()

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
                    self.PLAYLIST.append(cmd.data)
                    self.logger.log('QUEUE', {"location": location, "artist": artist, "title": title})

    def process_unqueue(self, cmd):
        try:
            index_at = cmd.data["index_at"]
        except KeyError as e:
            self.logger.log('error', str(e))
        else:
            self.playlist.pop(index_at)
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
            self.playlist = cmd.data
            self.PLAYLIST = cmd.data
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
