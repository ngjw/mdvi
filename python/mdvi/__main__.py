import os
import sys
import argparse
from multiprocessing import Process

from .server import app

def run(port):
    sys.stdout = sys.stderr = open(os.devnull, 'w')
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default='')
    parser.add_argument('-p', '--port', default=5000)
    pargs = parser.parse_args()

    p = Process(target=run, args=(pargs.port,))
    p.start()

    update_command = f'curl localhost:{pargs.port}/update?file=<afile>'

    os.system(
        'vim'
        f' --cmd "autocmd BufWritePost * silent !{update_command}"'
        f' --cmd "autocmd BufReadPost * silent !{update_command}"'
        f' {pargs.file}'
    )

    p.terminate()
