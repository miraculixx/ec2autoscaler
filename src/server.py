#
# Example where a pool of http servers share a single listening socket
#
# On Windows this module depends on the ability to pickle a socket
# object so that the worker processes can inherit a copy of the server
# object.  (We import `multiprocessing.reduction` to enable this pickling.)
#
# Not sure if we should synchronize access to `socket.accept()` method by
# using a process-shared lock -- does not seem to be necessary.
#
# Copyright (c) 2006-2008, R Oudkerk
# All rights reserved.
#
# Modified 2012-04:
#   - RequestHandler class responds 200 to ping and work, 404 to other paths.
#

import httplib
import os
import sys
import time

from random import randint
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler
from common import *

if sys.platform == 'win32':
    import multiprocessing.reduction    # make sockets pickable/inheritable

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.respond(httplib.OK, 'pong')
        elif self.path == '/work':
            self.work()
        else:
            self.respond(httplib.NOT_FOUND, "not found")

    # we override log_message() to show which process is handling the request
    def log_message(self, format, *args):
        note(format, *args)

    def respond(self, code, text):
        """ Respond with a text. """
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain')
        self.send_header("Content-Length", str(len(text)))
        self.end_headers()
        self.wfile.write(text)

    def work(self):
        """ Simulate computations. """
        start = time.time()
        complexity_ms = 450+randint(0, 100)
        w = int(0)
        while 1000*(time.time()-start) < complexity_ms:
            for i in xrange(0, 1000):
                w = w ^ i
                w = int(w * i) % 65536
        duration = time.time()-start
        self.log_message('w=%s\tduration=%s', w, duration)
        self.respond(httplib.OK, '%s\t%s' % (w, duration))


def serve_forever(server):
    note('starting server')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def runpool(address, number_of_processes):
    # create a single server object -- children will each inherit a copy
    server = HTTPServer(address, RequestHandler)

    # create child processes to act as workers
    for i in range(number_of_processes-1):
        Process(target=serve_forever, args=(server,)).start()

    # main process also acts as a worker
    serve_forever(server)


def test():
    ADDRESS = ('localhost', 30001)
    NUMBER_OF_PROCESSES = 5

    print 'Serving at http://%s:%d using %d worker processes' % \
          (ADDRESS[0], ADDRESS[1], NUMBER_OF_PROCESSES)
    print 'To exit press Ctrl-' + ['C', 'Break'][sys.platform=='win32']

    runpool(ADDRESS, NUMBER_OF_PROCESSES)


if __name__ == '__main__':
    freeze_support()
    f = open('/var/log/kasworker.log', "w")
    sys.stderr = f
    pidfile = '/var/run/kasworker.pid'
    fpid = open(pidfile, "w")
    fpid.write(str(os.getpid()))
    fpid.close()
    test()
    f.close()
    os.unlink(pidfile)