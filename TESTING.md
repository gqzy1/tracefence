# Reproducing the checks

Run `python -m unittest discover -s tests -v` with Python 3.12. Twelve checks passed locally and in GitHub Actions. The suite loads the production source with an explicit scripted host. It invokes the actual leader/validator callbacks with independent responses and checks control-flow leakage, unknown propagation, publication guards, failed model calls, conflicting interpretations and owner isolation.

These are local model fixtures. They do not execute GenVM Wasm or call an actual LLM. Official genvm-linter 0.11.0 passed; Stable Studio compiled the exact pinned production source. Four separate real transactions and finalized state readback are documented in [NETWORK.md](NETWORK.md).
