from . import models


def setup(env):
    request = env["request"]

    # start a transaction
    request.tm.begin()

    # inject some vars into the shell builtins
    env["tm"] = request.tm
    env["db_session"] = request.db_session
    env["models"] = models
