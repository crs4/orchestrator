# -*- coding:utf-8 -*-

from dispatcher import app

from flask.ext.script import Manager

from dispatcher.scripts import ResetDB, PopulateDB

from flask.ext.security.script import (CreateUserCommand , AddRoleCommand,
        RemoveRoleCommand, ActivateUserCommand, DeactivateUserCommand)

manager = Manager(app)
manager.add_command("reset_db", ResetDB())
manager.add_command("populate_db", PopulateDB())

manager.add_command('create_user', CreateUserCommand())
manager.add_command('add_role', AddRoleCommand())
manager.add_command('remove_role', RemoveRoleCommand())
manager.add_command('deactivate_user', DeactivateUserCommand())
manager.add_command('activate_user', ActivateUserCommand())

if __name__ == "__main__":
    manager.run()
