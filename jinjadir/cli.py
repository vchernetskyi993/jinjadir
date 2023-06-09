"""CLI of the application. Main entrypoint."""

import os
import re
from pathlib import Path
from typing import Annotated, Dict, Iterable, List, Optional, Set, Tuple, TypeVar

import typer
from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import flow
from returns.pointfree import bind
from returns.result import Failure, Result, Success
from rich.console import Console

_UNDEFINED_VAR_PATTERN = re.compile(r"'([\w]+)' is undefined")
_ARG_PATTERN = re.compile("^[^=]+=[^=]+$")

app = typer.Typer()
cwd = Path(os.getcwd())
stderr = Console(stderr=True)

Args = List[str]
ParsedArgs = Dict[str, str]


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
    processor = TemplateProcessor(templates_path, target_path)

    match flow(_arguments(arg if arg else []), bind(processor.process)):
        case Failure(error):
            stderr.print(error)
            raise typer.Exit(code=1)


class TemplateProcessor:
    """Class that processes Jinja templates."""

    def __init__(
        self,
        templates_path: Path,
        target_path: Path,
    ) -> None:
        """Create new processor.

        Parameters
        ----------
        templates_path : Path
            Path to templates directory.
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
        self.target_path = target_path

    def process(self, args: ParsedArgs) -> Result[None, str]:
        """Process templates.

        Parameters
        ----------
        args : ParsedArgs
            Templates arguments.

        Returns
        -------
        Result[None, str]
            None or error as string.
        """
        missing_variables: Set[str] = set()
        for template_path in self.env.list_templates():
            try:
                self._process_single(template_path, args)
            except UndefinedError as error:
                if error.message:
                    missing = _UNDEFINED_VAR_PATTERN.findall(error.message)[0]
                    missing_variables.add(missing)
        if missing_variables:
            return Failure(
                "{0} are required inside {1}.".format(
                    _format_error_values(missing_variables),
                    self.templates_path,
                ),
            )
        return Success(None)

    def _process_single(self, template_path: str, args: ParsedArgs) -> None:
        target_file = self.target_path / self.env.from_string(template_path).render(
            args,
        )
        os.makedirs(target_file.parent, exist_ok=True)
        target_file.write_text(
            self.env.get_template(template_path).render(args),
        )


def _arguments(args: Args) -> Result[ParsedArgs, str]:
    parsed_args = {arg: _argument(arg) for arg in args}

    if any(map(_is_nothing, parsed_args.values())):
        return Failure(
            "Invalid arguments format: {0}".format(
                _format_error_values(
                    arg
                    for arg, parsed_arg in parsed_args.items()
                    if _is_nothing(parsed_arg)
                ),
            ),
        )
    return Success(dict([arg.unwrap() for arg in parsed_args.values()]))


def _argument(pair_str: str) -> Maybe[Tuple[str, str]]:
    if not _ARG_PATTERN.match(pair_str):
        return Nothing
    pair = pair_str.split("=")
    return Some((pair[0], pair[1]))


def _format_error_values(error_values: Iterable[str]) -> str:
    return ",".join("'{0}'".format(missing) for missing in error_values)


_Type = TypeVar("_Type")


def _is_nothing(maybe: Maybe[_Type]) -> bool:
    return maybe == Nothing
