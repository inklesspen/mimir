import os
import sys
import transaction

from sqlalchemy import engine_from_config

from logging.config import dictConfig
from montague.loadwsgi import Loader

from ..models import (
    DBSession,
    MyModel,
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
    settings = loader.app_config(appname).config
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(model)
