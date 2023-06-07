"""CLI of the application. Main entrypoint."""

from typing import Annotated

import typer

app = typer.Typer()


@app.command(help="Print greeting.")
def main(
    name: Annotated[
        str,
        typer.Option(help="Name to greet."),
    ] = "World",
) -> None:
    print("Hello, {0}!".format(name))
