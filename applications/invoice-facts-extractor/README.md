# Invoice Facts Extractor

## Quickstart

This quickstart assumes you are using the devcontainer.

1. Install system requirements with: `bash setup.sh install`
2. Install Python dependencies with: `pip install -r requirements.txt`
   1. If you are using a Python virtual environment (venv), then load them before this and use the same terminal for the next commands.
3. Create a `.env`, set the `GOOGLE_API_KEY` variable, then source your `.env` file into your terminal.
4. Open the scripts directory with: `cd src/poc/`
5. Run `python3 extract.py`
   1. Verify a `.tsv` file was written to `examples/.poc/extract` for each of the examples.
6. Run `python3 synthesis.py`
   1. Verify a `.json` file was written to `examples/poc/synthesis` for each of the examples.
