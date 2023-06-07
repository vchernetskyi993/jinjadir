import os
from pathlib import Path

from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()


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
            "--arg",
            "name_arg={0}".format(name_arg),
            "--arg",
            "value_arg={0}".format(value_arg),
            "--arg",
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
    assert "'typer_version_arg'" in str(init_result.exception)
