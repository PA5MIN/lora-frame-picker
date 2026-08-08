# Contributing

1. Create a virtual environment with Python 3.9 or newer.
2. Install development dependencies: `python -m pip install -r requirements-dev.txt`.
3. Run `pytest` and `python packaging/audit_release.py` before opening a pull request.
4. Never commit personal media, models, network traces, local paths, credentials,
   session files, licenses, or generated output.

Bug reports should include the operating system, Python version, exact steps,
and sanitized error text. Do not attach private media or complete WebUI URLs.
