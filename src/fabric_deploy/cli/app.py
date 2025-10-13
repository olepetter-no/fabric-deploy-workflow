import click

from .commands.deploy import cmd as deploy_cmd
from .commands.validate import cmd as validate_cmd


@click.group(help="Microsoft Fabric deployment CLI")
def cli() -> None:
    pass


# register subcommands
cli.add_command(deploy_cmd, name="deploy")
cli.add_command(validate_cmd, name="validate")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
