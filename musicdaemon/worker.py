import signal

from daemon import MusicDaemon


class Worker:
    daemon = None

    def main(self):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        self.daemon = MusicDaemon()
        res = self.daemon.main()
        return res

    def stop(self, signum, frame):
        if self.daemon is not None:
            self.daemon.stop()
