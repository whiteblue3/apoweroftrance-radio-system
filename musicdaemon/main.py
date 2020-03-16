from master import Master
from daemon import MusicDaemon
from server import TCPServer

if __name__ == '__main__':
    master = Master([MusicDaemon, TCPServer])
    exit_code = master.main()
    exit(exit_code)
