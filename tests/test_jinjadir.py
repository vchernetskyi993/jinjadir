import os
from pathlib import Path

from typer.testing import CliRunner

from jinjadir.cli import app

_ARG_PARAM = "--arg"

runner = CliRunner(mix_stderr=False)


def test_initialize_cli_project(tmp_path: Path) -> None:
    # given
    templates_path = tmp_path / "templates"
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
    project_path = tmp_path / "my_app"
    os.mkdir(project_path)

    # when
    init_result = runner.invoke(
        app,
        [
            "--templates-path",
            str(templates_path),
            _ARG_PARAM,
            "name_arg={0}".format(name_arg),
            _ARG_PARAM,
            "value_arg={0}".format(value_arg),
            _ARG_PARAM,
            "typer_version_arg={0}".format(typer_version_arg),
            str(project_path),
        ],
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
    templates_path = tmp_path / "templates"
    os.mkdir(templates_path)
    requirements_template = "typer=={{ typer_version_arg }}"
    requirements_file = templates_path / "requirements.txt"
    (templates_path / requirements_file).write_text(requirements_template)
    project_path = tmp_path / "my_app"
    os.mkdir(project_path)

    # when
    init_result = runner.invoke(
        app,
        [
            "--templates-path",
            str(templates_path),
            str(project_path),
        ],
    )

    # then
    assert init_result.exit_code == 1
    assert "'typer_version_arg'" in init_result.stderr


def test_process_filename(tmp_path: Path) -> None:
    # given
    templates_path = tmp_path / "templates"
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
    init_result = runner.invoke(
        app,
        [
            "--templates-path",
            str(templates_path),
            _ARG_PARAM,
            "typer_version_arg={0}".format(typer_version_arg),
            _ARG_PARAM,
            "dir_name={0}".format(dir_name_arg),
            _ARG_PARAM,
            "env={0}".format(env_arg),
            str(project_path),
        ],
    )

    # then
    assert init_result.exit_code == 0
    output_requirements = "typer=={0}".format(typer_version_arg)
    output_file = "requirements-{0}.txt".format(env_arg)
    assert (
        project_path / dir_name_arg / output_file
    ).read_text() == output_requirements
