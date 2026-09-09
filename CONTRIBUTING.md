# Contributing

Install Python 3.12 and run `python -m pip install -r requirements-dev.txt`.
Run `ruff check .`, `ruff format --check .` and `pytest -q`.
Add behavior tests for every new route and every resource boundary; use synthetic
data and network/SDK doubles. Run an APIZIT local scan and record route counts.
Update the scenario README and global platform catalog. Never relax caps to
make a test pass. GitHub CI tests Windows and Linux; neither launches on AWS.
