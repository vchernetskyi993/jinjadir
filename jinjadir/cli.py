"""CLI of the application. Main entrypoint."""

import os
import re
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError

_UNDEFINED_VAR_PATTERN = re.compile(r"'([\w]+)' is undefined")

app = typer.Typer()
cwd = Path(os.getcwd())


@app.command(help="Copy and process Jinja templates to a target directory.")
def init(
    templates_path: Annotated[
        Path,
        typer.Option(help="Path to directory with Jinja templates."),
    ],
    target_path: Annotated[
        Path,
        typer.Argument(help="Path to unpack source templates."),
    ] = cwd,
    arg: Annotated[
        Optional[list[str]],
        typer.Option(
            help="""
                Jinja2 variables in the form <key>=<value>.
                To pass multiple args use '--arg' repeatably
                (e.g. --arg k0=v0 --arg k1=v1).
            """,
        ),
    ] = None,
) -> None:
    os.makedirs(target_path, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=True,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    missing_variables = set()
    for template_path in env.list_templates():
        try:
            target_file = target_path / env.from_string(template_path).render(
                _arguments(arg),
            )
            os.makedirs(target_file.parent, exist_ok=True)
            target_file.write_text(
                env.get_template(template_path).render(_arguments(arg)),
            )
        except UndefinedError as error:
            if error.message:
                missing = _UNDEFINED_VAR_PATTERN.findall(error.message)[0]
                missing_variables.add(missing)
    if missing_variables:
        print(
            "{0} are required inside {1}.".format(
                ",".join("'{0}'".format(missing) for missing in missing_variables),
                templates_path,
            ),
            file=sys.stderr,
        )
        raise typer.Exit(code=1)


def _arguments(args: Optional[list[str]]) -> dict[str, str]:
    if not args:
        return {}
    return dict([_argument(arg) for arg in args])


def _argument(pair: str) -> tuple[str, str]:
    (name, value) = pair.split("=")
    return (name, value)