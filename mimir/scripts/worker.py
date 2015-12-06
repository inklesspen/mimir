import sys

import argparse
from logging.config import dictConfig
from logging import getLogger
from montague.loadwsgi import Loader
from pyramid.scripting import prepare

from ..models import Credential
from ..lib.fetch import determine_fetches, fetch_thread_page
from ..lib.split import extract_posts_from_pages

log = getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('config_uri')
parser.add_argument('appname')


def do_fetch(request):
    cred = request.db_session.query(Credential).filter_by(valid=True).one()
    fetches = determine_fetches(request.db_session, cred)
    for thread_id, page_num in fetches:
        fetch_thread_page(request.db_session, cred, thread_id, page_num)

    extract_posts_from_pages(request.db_session)
    request.tm.commit()


def main(argv=sys.argv):
    args = parser.parse_args(argv[1:])
    loader = Loader(args.config_uri)
    dictConfig(loader.logging_config(args.appname))
    app = loader.load_app(args.appname)
    env = prepare(registry=app.registry)
    try:
        do_fetch(env['request'])
    finally:
        env['closer']()
