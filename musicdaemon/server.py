import sys
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from logger import Logger


class TCPHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.log_message("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

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
        self.httpd = ThreadedHTTPServer(server_address, TCPHandler)

    def main(self):
        self.logger.log('start', 'Starting HTTP Server...\n')

        while not self.__stop:
            sys.stdout.flush()
            self.httpd.handle_request()

        self.logger.log('stop', 'Stopping HTTP Server...\n')
        self.httpd.server_close()
        return 0

    def stop(self):
        self.__stop = True
