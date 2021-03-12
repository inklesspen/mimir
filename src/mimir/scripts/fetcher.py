import argparse
import sys

from pyramid.paster import bootstrap, setup_logging

from ..lib.fetch import determine_fetches, fetch_thread_page, validate_cred
from ..lib.split import extract_posts_from_pages
from ..models import Credential


description = "Fetch the latest threads from SA."

parser = argparse.ArgumentParser(
    description=description,
)
parser.add_argument(
    "config_uri",
    help="The URI to the configuration file.",
)


def fetch_threads(db_session):
    cred = db_session.query(Credential).filter_by(valid=True).one()
    validate_cred(cred)
    if not cred.valid:
        raise ValueError("Cred invalid")
    fetches = determine_fetches(db_session, cred)
    for thread_id, page_num in fetches:
        fetch_thread_page(db_session, cred, thread_id, page_num)

    extract_posts_from_pages(db_session)


def main(argv=sys.argv):
    args = parser.parse_args(argv[1:])
    setup_logging(args.config_uri)
    with bootstrap(args.config_uri) as env:
        env["request"].tm.begin()
        fetch_threads(env["request"].db_session)
        env["request"].tm.commit()
