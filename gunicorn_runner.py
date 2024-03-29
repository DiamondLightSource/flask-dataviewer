# This gist shows how to integrate Flask into a 
# custom Gunicorn-WSGI application described
# here: http://docs.gunicorn.org/en/stable/custom.html
#
# Required to run multiple worker threads via the dials.python interpreter..
from __future__ import unicode_literals
import os

# To run with DIALS we need to add local packages to the path
# DIALS overwrites PYTHONPATH so use  PYTHONPATH_EXT environment variable for local packages
import sys

sys.path.append(os.environ.get('PYTHONPATH_EXT'))

import gunicorn.app.base

from app import create_app

# Create the Flask App from app module
app = create_app()

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                       if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        master_pid = os.getppid()
        pid_file = os.environ.get('PIDFILE', 'image-service.pid')

        with open(pid_file, 'w') as f:
            f.write("%s" % format(master_pid))

        return self.application


if __name__ == '__main__':
    # Adding arguments to emulate gunicorn app startup
    import argparse

    parser = argparse.ArgumentParser(description='HDF5 Image Service')
    parser.add_argument('--workers', type=int, help='number of worker processes')
    parser.add_argument('--host', help='Host (default localhost)', default='127.0.0.1')
    parser.add_argument('--port', type=int, dest='port',help='Port (default 5000)', default=5000)

    args = parser.parse_args()

    options = {
        'bind': '%s:%d' % (args.host, args.port),
        'workers': args.workers,
    }

    StandaloneApplication(app, options).run()
