import sys
import os
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from command import CMD
from logger import Logger


class TCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))

        if self.server.logger is not None:
            self.server.logger.log("HTTPStream", format % args)

    def queue_cmd(self, cmd):
        if self.server.cmd_queue is not None:
            self.server.logger.log("CMD SEND", cmd)
            self.server.cmd_queue.put(cmd)

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.log_message("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

        cmd = CMD(host="server", target="daemon", command="GET", data="")
        self.queue_cmd(cmd)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])    # <--- Gets the size of data
        post_data = self.rfile.read(content_length)             # <--- Gets the data itself
        self.log_message("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                         str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class TCPServer:
    httpd = None
    __stop = False

    def __init__(self):
        self.__stop = False
        self.logger = Logger('HTTPServer')

        server_address = ('0.0.0.0', 9000)

        self.httpd = HTTPServer(server_address, TCPHandler)

    def main(self, cmd_queue=None):
        self.logger.log('start', {
            'pid': os.getpid(),
            'message': 'Starting HTTP Server...\n'
        })
        self.httpd.logger = self.logger
        self.httpd.cmd_queue = cmd_queue

        while not self.__stop:
            sys.stdout.flush()
            self.httpd.handle_request()
        return 0

    def stop(self):
        self.__stop = True

        self.logger.log('stop', {
            'pid': os.getpid(),
            'message': 'Stopping HTTP Server...\n'
        })
        self.httpd.shutdown()