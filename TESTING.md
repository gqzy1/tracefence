# Reproducing the checks

Run `python -m unittest discover -s tests -v` with Python 3.12. The suite loads the production source with an explicit scripted host. It invokes the actual leader/validator callbacks with independent responses and checks control-flow leakage, unknown propagation, publication guards, failed model calls, conflicting interpretations and owner isolation.

These are local model fixtures. They do not execute GenVM Wasm, call an actual LLM, establish Studio compatibility or prove network consensus. The GitHub workflow runs these same checks without sending any transactions. No deployment or accepted consensus evidence is recorded.
