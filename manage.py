#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask.ext.script import Manager, Shell
from app import app

manager = Manager(app)


def main():
    pass


def make_shell_context():
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def deploy():
    """Run deployment tasks."""
    pass


if __name__ == '__main__':
    # app()
    manager.run()
