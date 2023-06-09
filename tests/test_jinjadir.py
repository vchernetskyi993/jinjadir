import os
from itertools import chain
from pathlib import Path
from typing import Optional

import pytest
from click.testing import Result
from typer.testing import CliRunner

from jinjadir.cli import app

_ARG_PARAM = "--arg"
_TEMPLATES_PARAM = "--templates-path"

runner = CliRunner(mix_stderr=False)


def test_initialize_cli_project(tmp_path: Path) -> None:
    # given
    templates_path = _templates_path(tmp_path)
    os.mkdir(templates_path)
    conf_file = "config.conf"
    input_conf_path = templates_path / conf_file
    name_arg = "confname"
    value_arg = "value0"
    conf_template = """
    {{ name_arg }} {
        key = "{{ value_arg }}"
        key1 = "value1"
    }
    """
    input_conf_path.write_text(conf_template)
    typer_version_arg = "1.3.2"
    requirements_template = "typer=={{ typer_version_arg }}"
    inner_dir = "more-configs"
    inner_dir_path = templates_path / inner_dir
    os.mkdir(inner_dir_path)
    requirements_file = Path(inner_dir) / "requirements.txt"
    (templates_path / requirements_file).write_text(requirements_template)
    (inner_dir_path / conf_file).write_text(conf_template)
    project_path = _project_path(tmp_path)
    os.mkdir(project_path)

    # when
    init_result = _invoke(
        tmp_path,
        "name_arg={0}".format(name_arg),
        "value_arg={0}".format(value_arg),
        "typer_version_arg={0}".format(typer_version_arg),
    )

    # then
    assert init_result.exit_code == 0
    output_conf_template = """
    {0} {{
        key = "{1}"
        key1 = "value1"
    }}
    """
    output_conf = output_conf_template.format(name_arg, value_arg)
    assert (project_path / conf_file).read_text() == output_conf
    output_requirements = "typer=={0}".format(typer_version_arg)
    assert (project_path / requirements_file).read_text() == output_requirements
    assert (project_path / inner_dir / conf_file).read_text() == output_conf


def test_throw_on_unknown_placeholder(tmp_path: Path) -> None:
    # given
    templates_path = _templates_path(tmp_path)
    os.mkdir(templates_path)
    requirements_template = "typer=={{ typer_version_arg }}"
    requirements_file = templates_path / "requirements.txt"
    (templates_path / requirements_file).write_text(requirements_template)
    project_path = _project_path(tmp_path)
    os.mkdir(project_path)

    # when
    init_result = _invoke(tmp_path)

    # then
    assert init_result.exit_code == 1
    assert "'typer_version_arg'" in init_result.stderr


def test_process_filename(tmp_path: Path) -> None:
    # given
    templates_path = _templates_path(tmp_path)
    os.mkdir(templates_path)
    typer_version_arg = "1.11.0"
    dir_name_arg = "requirements"
    env_arg = "dev"
    requirements_template = "typer=={{ typer_version_arg }}"
    inner_dir = "{{ dir_name }}"
    inner_dir_path = templates_path / inner_dir
    os.mkdir(inner_dir_path)
    requirements_file = Path(inner_dir) / "requirements-{{ env }}.txt"
    (templates_path / requirements_file).write_text(requirements_template)
    project_path = tmp_path / "testapp"
    os.mkdir(project_path)

    # when
    init_result = _invoke(
        tmp_path,
        "typer_version_arg={0}".format(typer_version_arg),
        "dir_name={0}".format(dir_name_arg),
        "env={0}".format(env_arg),
        project_path=project_path,
    )

    # then
    assert init_result.exit_code == 0
    output_requirements = "typer=={0}".format(typer_version_arg)
    output_file = "requirements-{0}.txt".format(env_arg)
    assert (
        project_path / dir_name_arg / output_file
    ).read_text() == output_requirements


@pytest.mark.parametrize(
    "arg_value",
    ["no-equals", "too=many=equals", "=empty-key", "empty-value="],
)
def test_throw_on_wrong_arg_format(tmp_path: Path, arg_value: str) -> None:
    # given
    templates_path = _templates_path(tmp_path)
    os.mkdir(templates_path)
    conf_file = "config.conf"
    input_conf_path = templates_path / conf_file
    conf_template = """
    conf {
        key = "value"
        key1 = "value1"
    }
    """
    input_conf_path.write_text(conf_template)
    project_path = _project_path(tmp_path)
    os.mkdir(project_path)

    # when
    init_result = _invoke(tmp_path, arg_value)

    # then
    assert init_result.exit_code == 1
    assert "'{0}'".format(arg_value) in init_result.stderr


def _templates_path(tmp_path: Path) -> Path:
    return tmp_path / "templates"


def _project_path(tmp_path: Path) -> Path:
    return tmp_path / "my_app"


def _invoke(tmp_path: Path, *args: str, project_path: Optional[Path] = None) -> Result:
    return runner.invoke(
        app,
        [
            _TEMPLATES_PARAM,
            str(_templates_path(tmp_path)),
            *chain(*[[_ARG_PARAM, arg] for arg in args]),
            str(project_path if project_path else _project_path(tmp_path)),
        ],
    )
