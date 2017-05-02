"""exec module for the cli."""
import click

from iocage.lib.ioc_common import logit
from iocage.lib.ioc_exec import IOCExec
from iocage.lib.ioc_list import IOCList

__rootcmd__ = True


@click.command(context_settings=dict(
    ignore_unknown_options=True, ),
    name="exec", help="Run a command inside a specified jail.")
@click.option("--host_user", "-u", default="root",
              help="The host user to use.")
@click.option("--jail_user", "-U", help="The jail user to use.")
@click.argument("jail", required=True, nargs=1)
@click.argument("command", nargs=-1, type=click.UNPROCESSED)
def cli(command, jail, host_user, jail_user):
    """Runs the command given inside the specified jail as the supplied
    user."""
    # We may be getting ';', '&&' and so forth. Adding the shell for safety.
    if len(command) == 1:
        command = ("/bin/sh", "-c") + command

    if jail.startswith("-"):
        logit({
            "level"  : "ERROR",
            "message": "Please specify a jail first!"
        })
        exit(1)

    if host_user and jail_user:
        logit({
            "level"  : "ERROR",
            "message": "Please only specify either host_user or"
                       " jail_user, not both!"
        })
        exit(1)

    jails, paths = IOCList("uuid").list_datasets()
    _jail = {tag: uuid for (tag, uuid) in jails.items() if
             uuid.startswith(jail) or tag == jail}

    if len(_jail) == 1:
        tag, uuid = next(iter(_jail.items()))
        path = paths[tag]
    elif len(_jail) > 1:
        logit({
            "level"  : "ERROR",
            "message": f"Multiple jails found for {jail}:"
        })
        for t, u in sorted(_jail.items()):
            logit({
                "level"  : "ERROR",
                "message": f"  {u} ({t})"
            })
        exit(1)
    else:
        logit({
            "level"  : "ERROR",
            "message": "{} not found!".format(jail)
        })
        exit(1)

    msg, err = IOCExec(command, uuid, tag, path, host_user,
                       jail_user).exec_jail()

    if err:
        logit({
            "level"  : "ERROR",
            "message": err.decode()
        })
    else:
        logit({
            "level"  : "INFO",
            "message": msg.decode("utf-8")
        })
