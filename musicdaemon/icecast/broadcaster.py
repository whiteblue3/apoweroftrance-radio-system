# -*- coding: utf-8 -*-
# Inspired by https://github.com/turlando/airhead/blob/master/airhead/broadcaster.py
import logging
import os
import sys

import click
import shouty

logger = logging.getLogger('[broadcaster]')


class Broadcaster(object):
    def __init__(self, conf, playlist, mount, loop=True):
        self._playlist = self._load_playlist(playlist)
        self.current_playlist = self._playlist[:]
        self._loop = loop
        self._mount = mount
        self._params = {
            'format': shouty.Format.MP3,
            'mount': '/' + mount,
            'audio_info': {
                'samplerate': '44100',
                'channels': '2',
                'quality': '6'
            }
        }
        self._params.update(conf)

    def _load_playlist(self, playlist):
        with open(playlist, 'r') as fd:
            return [x.strip() for x in fd.readlines() if x.strip()]

    def _send_file(self, connection, file_name):
        with open(file_name, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                connection.send(chunk)
                connection.sync()

    def run(self):
        with shouty.connect(**self._params) as connection:
            while True:
                try:
                    filepath = self.current_playlist.pop()
                except IndexError:
                    logger.info('Playlist finished...')
                    if self._loop:
                        self.current_playlist = self._playlist[:]
                        continue
                    break
                else:
                    logger.info('Sending {}'.format(filepath))
                    self._send_file(connection, str(filepath))


CONF = {
    'user': 'source'
}
VARS = (
    ('ICECAST_HOST', 'host'),
    ('ICECAST_PORT', 'port'),
    ('ICECAST_SOURCE_PASSWORD', 'password'),
)


def load_conf():
    conf = CONF.copy()
    for k, v in VARS:
        conf[v] = os.getenv(k)
        if v == 'port':
            conf[v] = int(conf[v])
        if not conf[v]:
            logger.error('{} MISSING'.format(k))
            sys.exit(0)
    return conf


@click.command()
@click.option('--playlist')
@click.option('--mount')
def stream_it(playlist, mount):
    conf = load_conf()
    bc = Broadcaster(conf, playlist, mount)
    bc.run()


if __name__ == '__main__':
    stream_it()