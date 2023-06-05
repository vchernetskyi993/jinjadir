"""CLI of the application. Main entrypoint."""

import os
from pathlib import Path
from typing import Annotated, List, Optional

import typer

app = typer.Typer()
cwd = Path(os.getcwd())


@app.command()
def init(
    templates_path: Annotated[Path, typer.Option()],
    target_path: Annotated[Path, typer.Argument()] = cwd,
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
    """
    Initialize new project.

    Parameters
    ----------
    target_path : Path
        Path to a new project directory.

    templates_path : Path
        Path to a directory with project templates.

    arg : List[str]
        List of key value pairs that will be used as Jinja2 variables.
    """
    pass
