# {{ project }}

CLI app created using jinjadir.

## Usage

Create and activate virtual environment the way you like.

Install {{ project }}: `pip install .`.

Use CLI: `{{ project }} --help`.

## Development

Install dev requirements: `pip install -r requirements/dev.txt`.

Install package in editable way: `pip install -e .`.

Format code: `black .`.

Sort imports: `isort .`.

Remove unused imports: `autoflake .`.

Lint code: `flake8`.

Check types: `mypy .`.

Test code: `pytest`.
