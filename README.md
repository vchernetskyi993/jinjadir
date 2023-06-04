# Python Scaffold

Personal utility to initialize Python based projects.

## Usage

Create and activate virtual environment the way you like.

Install dependencies: `pip install -r requirements.txt`.

Install scaffold: `pip install .`.

Create empty directory for you future project wherever you like: `mkdir myapp && cd myapp`.

Initialize Python project: `pp init`.

## Development

Install dev requirements: `pip install -r requirements/dev.txt`.

Install package in editable way: `pip install -e .`.

Format code: `black .`.

Sort imports: `isort .`.

Remove unused imports: `autoflake .`.

Lint code: `flake8`.

Check types: `mypy .`.

Test code: `pytest`.
