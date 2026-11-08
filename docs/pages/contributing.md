# Contributing

Contributions are welcome, especially **new handlers** (see [Extending WebGrep](extending.md)) and bug reports.

## Reporting issues

Open an issue on [GitHub](https://github.com/dhondta/webgrep/issues) and include:

- the WebGrep version (`webgrep --version`);
- the exact command and its output, ideally with `--verbose`;
- if possible, the URL (or a minimal Web page) that shows the issue.

## Security

Please do **not** report vulnerabilities in public issues. See the [security policy](https://github.com/dhondta/webgrep/blob/main/SECURITY.md): report them privately through the repository's *Security* tab (*Report a vulnerability*).

Dependencies are monitored by Dependabot and audited with [pip-audit](https://github.com/pypa/pip-audit) by the `security` workflow (`.github/workflows/security.yml`), on every push and pull request to `main` and weekly.

## Development setup

```console
$ git clone https://github.com/dhondta/webgrep
$ cd webgrep
$ pip install -e .
$ pip install flake8 pytest pytest-cov
$ flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
$ pytest --cov=webgrep
```

The tests serve a sample Web page from a local HTTP server and run `webgrep` on it. The optional tools (see [Installation](installation.md#optional-tools)) are not required, but they make the tests cover the image handlers.

CI (`.github/workflows/python-package.yml`) installs the package on Python 3.10 to 3.13, runs the flake8 check and the tests, and publishes the coverage badge.

## Releasing

The version is stored in `src/webgrep/VERSION.txt`. On each push to `main`, CI checks whether that version is already on PyPI. If it is not, CI builds the package and publishes it.

## Building this documentation

```console
$ pip install -r docs/requirements.txt
$ mkdocs serve -f docs/mkdocs.yml          # live preview at http://127.0.0.1:8000
$ mkdocs build --strict -f docs/mkdocs.yml # what Read the Docs runs
```

Read the Docs builds the site from `.readthedocs.yaml` at the root of the repository.
