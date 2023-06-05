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
    conf = """
    {{ name_arg }} {
        key = "{{ value_arg }}"
        key1 = "value1"
    }
    """
    input_conf_path.write_text(conf)
    # add 1 dir
    # add 2 files in dir
    # other arg
    # same arg in other file
    # invalid arg
    project_path = tmp_path / "my_app"
    os.mkdir(project_path)
    os.chdir(project_path)

    # when
    init_result = runner.invoke(
        app,
        [
            "init",
            "--templates-path",
            str(templates_path),
            "--arg",
            "name_arg=confname",
            "--arg",
            "value_arg=value0",
        ],
    )

    # then
    assert init_result.exit_code == 0
    # validate project directory
