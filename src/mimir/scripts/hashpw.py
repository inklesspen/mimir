import getpass

from mimir.security import Account


def main():
    username = input("Username: ")
    password = getpass.getpass()
    hashed = Account.hash_pw(password)
    print("{}:{}".format(username, hashed))
