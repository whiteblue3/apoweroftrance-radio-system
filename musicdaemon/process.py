import signal


class Process:
    """Sub Process"""
    process = None

    def main(self, process_class, cmd_queue=None):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        self.process = process_class()
        res = self.process.main(cmd_queue)
        return res

    def stop(self, signum, frame):
        if self.process is not None:
            self.process.stop()
