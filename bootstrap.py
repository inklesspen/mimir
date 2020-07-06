#!/usr/bin/env python3

import argparse
import subprocess
import sys


def is_venv():
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def update_deps():
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip-tools",
            "pip",
            "setuptools",
            "wheel",
        ]
    )
    subprocess.check_call(
        [
            "pip-compile",
            "--upgrade",
            "--build-isolation",
            "--generate-hashes",
            "--output-file",
            "requirements/main.txt",
            "requirements/main.in",
        ]
    )
    subprocess.check_call(
        [
            "pip-compile",
            "--upgrade",
            "--build-isolation",
            "--generate-hashes",
            "--output-file",
            "requirements/dev.txt",
            "requirements/dev.in",
        ]
    )


def init():
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "-r",
            "requirements/main.txt",
            "-r",
            "requirements/dev.txt",
        ]
    )
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--editable", "."])
    subprocess.check_call(["rm", "-rf", ".tox"])


def update():
    update_deps()
    init()


COMMANDS = {
    "update-deps": update_deps,
    "init": init,
    "update": update,
}


parser = argparse.ArgumentParser()
parser.add_argument("command", choices=COMMANDS.keys(), nargs="?", default="update")


if __name__ == "__main__":
    if is_venv():
        # main()
        arguments = parser.parse_args()
        COMMANDS[arguments.command]()
    else:
        print("This script must be run within an activated virtualenv.")
