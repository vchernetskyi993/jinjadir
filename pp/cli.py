"""CLI of the application. Main entrypoint."""

import os
from pathlib import Path
from typing import Annotated, List, Optional

import typer

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
        Optional[List[str]],
        typer.Option(
            help="""
                Jinja2 variables in the form <key>=<value>.
                To pass multiple args use '--arg' repeatably
                (e.g. --arg k0=v0 --arg k1=v1).
            """,
        ),
    ] = None,
) -> None:
    pass
