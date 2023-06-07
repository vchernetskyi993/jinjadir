from typer.testing import CliRunner

from {{ project }}.cli import app

runner = CliRunner()


def test_main() -> None:
    # given
    name = "John"

    # when
    init_result = runner.invoke(app, ["--name", name])

    # then
    assert init_result.exit_code == 0
    assert init_result.stdout == "Hello, John!\n"
