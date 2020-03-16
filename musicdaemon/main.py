from master import Master
from daemon import MusicDaemon
from server import TCPServer


class Child:
    name = None
    process_class = None

    def __init__(self, name, process_class):
        self.name = name
        self.process_class = process_class


if __name__ == '__main__':
    yui = Child(name="yui", process_class=MusicDaemon)
    server = Child(name="server", process_class=TCPServer)

    master = Master([yui, server])
    exit_code = master.main()
    exit(exit_code)
