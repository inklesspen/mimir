import os
import sys
import transaction

from logging.config import dictConfig
from montague.loadwsgi import Loader
from pyramid.scripting import prepare

from ..models import (
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> appname\n'
          '(example: "%s config.toml development")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 3:
        usage(argv)
    config_uri = argv[1]
    appname = argv[2]
    loader = Loader(config_uri)
    dictConfig(loader.logging_config(appname))
    app = loader.load_app(appname)
    env = prepare(registry=app.registry)
    env['app'] = app
    try:
        engine = env['request'].db_session.bind
        Base.metadata.create_all(engine)
    finally:
        env['closer']()
