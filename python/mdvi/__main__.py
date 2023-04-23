import os
import socket
import argparse
from multiprocessing import Process

from .server import app, run

parser = argparse.ArgumentParser()
parser.add_argument('file', nargs='?', default='')
parser.add_argument('-p', '--port', default=5000)
pargs = parser.parse_args()

p = Process(target=run, args=(pargs.port,))
p.start()

update_command = f'curl localhost:{pargs.port}/update?file=<afile>'

host = socket.gethostname()
message = f'mdvi running on http://{host}:{pargs.port}'
hr = len(message) * '='

os.system(
    'vim'
    f' --cmd "autocmd BufWritePost * silent !{update_command}"'
    f' --cmd "autocmd BufReadPost * silent !{update_command}"'
    f' --cmd "echom \' \'"'
    f' --cmd "echom \'{hr}\'"'
    f' --cmd "echom \'{message}\'"'
    f' --cmd "echom \'{hr}\'"'
    f' --cmd "echom \' \'"'
    f' {pargs.file}'
)

p.terminate()
