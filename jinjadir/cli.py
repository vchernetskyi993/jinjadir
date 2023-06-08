"""CLI of the application. Main entrypoint."""

import os
import re
import sys
from pathlib import Path
from typing import Annotated, List, Optional, Set, Tuple

import typer
from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError
from returns.result import Failure, Result, Success

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
    os.makedirs(target_path, exist_ok=True)
    match TemplateProcessor(templates_path, arg if arg else [], target_path).process():
        case Failure(error):
            print(error, file=sys.stderr)  # noqa: WPS421
            raise typer.Exit(code=1)


class TemplateProcessor:
    """Class that processes Jinja templates."""

    def __init__(
        self,
        templates_path: Path,
        args: List[str],
        target_path: Path,
    ) -> None:
        """Create new processor.

        Parameters
        ----------
        templates_path : Path
            Path to templates directory.
        args : List[str]
            Arguments in a form <key>=<value>.
        target_path : Path
            Path to target directory.
        """
        self.templates_path = templates_path
        self.env = Environment(
            loader=FileSystemLoader(templates_path),
            autoescape=True,
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )
        self.args = args
        self.target_path = target_path
        self.missing_variables: Set[str] = set()

    def process(self) -> Result[None, str]:
        """Process templates.

        Returns
        -------
        Result[None, str]
            None or error as string.
        """
        for template_path in self.env.list_templates():
            try:
                self._process_single(template_path)
            except UndefinedError as error:
                if error.message:
                    missing = _UNDEFINED_VAR_PATTERN.findall(error.message)[0]
                    self.missing_variables.add(missing)
        if self.missing_variables:
            return Failure(
                "{0} are required inside {1}.".format(
                    ",".join(
                        "'{0}'".format(missing) for missing in self.missing_variables
                    ),
                    self.templates_path,
                ),
            )
        return Success(None)

    def _process_single(self, template_path: str) -> None:
        target_file = self.target_path / self.env.from_string(template_path).render(
            _arguments(self.args),
        )
        os.makedirs(target_file.parent, exist_ok=True)
        target_file.write_text(
            self.env.get_template(template_path).render(_arguments(self.args)),
        )


def _arguments(args: List[str]) -> dict[str, str]:
    return dict([_argument(arg) for arg in args])


def _argument(pair_str: str) -> Tuple[str, str]:
    # TODO: validate format
    pair = pair_str.split("=")
    return (pair[0], pair[1])
