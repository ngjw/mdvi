import os
import socket
import argparse
from multiprocessing import Process
from contextlib import contextmanager

from .server import run

class Editor:

    def __init__(self, port):
        self.port = port

    @property
    def hostname(self):
        return socket.gethostname()

    @contextmanager
    def server(self):
        server_proc = Process(target=run, args=(self.port,))
        server_proc.start()
        try:
            yield
        finally:
            server_proc.terminate()

    @property
    def welcome_message(self):
        message = f'mdvi running on http://{self.hostname}:{self.port}'
        hr = len(message) * '='

        lines = [' ', hr, message, hr, ' ']
        return ' '.join(f' --cmd "echo \'{line}\'"' for line in lines)

    @property
    def events(self):
        update_command = f"silent write !curl localhost:{self.port}/update -X POST -H 'Content-Type: application/json\' --data-binary @-"
        events = ['BufEnter', 'BufWritePost', 'InsertLeave']
        return ' '.join(f' --cmd "autocmd {event} * {update_command}"' for event in events)

    def run(self):
        with self.server():
            os.system(f"vim {self.welcome_message} {self.events} {pargs.file}")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default='')
    parser.add_argument('-p', '--port', default=5000)
    pargs = parser.parse_args()

    editor = Editor(port=pargs.port)
    editor.run()
