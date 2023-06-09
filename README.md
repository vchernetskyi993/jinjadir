# Jinja Directory

Utility to unpack directory of [Jinja](https://jinja.palletsprojects.com/en) templates.
Useful for scaffolding of projects with predefined structure.

## Usage

Create and activate virtual environment the way you like.

Install jinjadir: `pip install .`.

Initialize example Python CLI project: 
```shell
jinjadir \
    --templates-path <path to this repo>/templates/cli \
    --arg project=my_app \
    myapp/
```

## Development

Install dev requirements: `pip install -r requirements/dev.txt`.

Install package in editable way: `pip install -e .`.

Format code: `black .`.

Sort imports: `isort .`.

Remove unused imports: `autoflake .`.

Lint code: `flake8`.

<!-- FIXME: exclude templates folder -->
Check types: `mypy .`.

Test code: `pytest`.
