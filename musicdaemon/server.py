import sys
import os
import json
from dateutil.parser import parse
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from command import CMD, COMMAND_LIST, QUEUE, UNQUEUE
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

    def _set_response(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.log_message("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

        request_path = str(self.path)

        cmd = CMD(host=self.server.name, target="yui", command="GET", data=request_path)
        self.queue_cmd(cmd)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])    # <--- Gets the size of data
        post_data = self.rfile.read(content_length)             # <--- Gets the data itself
        self.log_message("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                         str(self.path), str(self.headers), post_data.decode('utf-8'))

        # request_path = str(self.path)
        data = json.loads(post_data.decode('utf-8'))

        host = data["host"]
        if host is None or host is "":
            host = self.server.name

        target = data["target"]
        if target is None or target is "":
            target = "yui"

        command = data["command"]
        payload = data["data"]
        if (
            command is None or command is "" or payload is None or payload is ""
        ) or (
            command not in COMMAND_LIST
        ):
            self._set_response(400)
            self.wfile.write("Bad Request".encode('utf-8'))
            return

        if command == QUEUE:
            if self.validate_queue_command(data) is False:
                self._set_response(400)
                self.wfile.write("Request is invalid queue command".encode('utf-8'))
                return
        elif command == UNQUEUE:
            if self.validate_unqueue_command(data) is False:
                self._set_response(400)
                self.wfile.write("Request is invalid unqueue command".encode('utf-8'))
                return

        cmd = CMD(host=host, target=target, command=command, data=payload)
        self.queue_cmd(cmd)

        self._set_response()
        self.wfile.write("OK".encode('utf-8'))

    def validate_queue_command(self, data):
        command = data["command"]
        payload = data["data"]

        if command not in QUEUE:
            self.log_message("Not a queue command")
            return False

        try:
            _ = payload["track_id"]
        except KeyError as e:
            self.log_message("'track_id' is a must have requirement")
            return False

        try:
            queue_at = payload["queue_at"]
        except KeyError:
            queue_at = None

        if queue_at is not None:
            try:
                parse(queue_at, fuzzy=False)
            except ValueError:
                self.log_message("'queue_at' is invalid datetime format")
                return False

        return True

    def validate_unqueue_command(self, data):
        command = data["command"]
        payload = data["data"]

        if command not in UNQUEUE:
            self.log_message("Not a unqueue command")
            return False

        try:
            _ = payload["track_id"]
        except KeyError:
            self.log_message("'track_id' is a must have requirement")
            return False

        return True


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class TCPServer:
    name = None
    httpd = None
    __stop = False

    def __init__(self, name):
        self.name = name
        self.__stop = False
        self.logger = Logger(TCPServer.__name__, name)

        server_address = ('0.0.0.0', 9000)

        self.httpd = ThreadedHTTPServer(server_address, TCPHandler)

    def main(self, cmd_queue=None):
        self.logger.log('start', {
            'pid': os.getpid(),
            'message': 'Starting HTTP Server...\n'
        })
        self.httpd.logger = self.logger
        self.httpd.name = self.name
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
