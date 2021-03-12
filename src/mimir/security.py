import attr
from passlib.hash import argon2
from pyramid.authentication import AuthTktCookieHelper
from pyramid.security import Allowed, Denied
from pyramid.settings import aslist


class MimirSecurityPolicy:
    def __init__(self, secret):
        self.helper = AuthTktCookieHelper(secret=secret, secure=True)

    def identity(self, request):
        """ Return app-specific user object. """
        ticket = self.helper.identify(request)
        if ticket is None:
            return None
        for account in request.accounts:
            if account.username == ticket["userid"]:
                return account.username
        return None

    def authenticated_userid(self, request):
        """ Return a string ID for the user. """
        return self.identity(request)

    def permits(self, request, context, permission):
        """ Allow access to everything if signed in. """
        identity = self.identity(request)
        if identity is not None:
            return Allowed("User is signed in.")
        else:
            return Denied("User is not signed in.")

    def remember(self, request, userid, **kw):
        return self.helper.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.helper.forget(request, **kw)


@attr.s(auto_attribs=True, frozen=True)
class Account:
    username: str
    hashed: str

    def verify_pw(self, password: str) -> bool:
        return argon2.verify(password, self.hashed)

    @staticmethod
    def hash_pw(password: str) -> str:
        return argon2.hash(password)


def request_accounts(request):
    return [
        Account(*x.split(":", 1))
        for x in aslist(request.registry.settings["auth.accounts"])
    ]


def request_check_login(request, username, password):
    for account in request.accounts:
        if account.username == username and account.verify_pw(password):
            return True
    return False


def includeme(config):
    config.add_request_method(request_accounts, "accounts", reify=True)
    secret = config.get_settings()["auth.secret"]
    config.set_security_policy(MimirSecurityPolicy(secret))
    config.add_request_method(request_check_login, "check_login")
