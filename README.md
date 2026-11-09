# TraceFence

**Where can restricted information reach an output?**

TraceFence implements a bounded information-flow audit for declared data-processing pipelines. A public constant can still reveal a private fact when that fact controls whether the constant is emitted. The analysis therefore distinguishes value dependencies from control dependencies.

## The model

A plan contains 1–4 restriction labels, 2–8 ordered nodes, and 1–4 output policies. Each node has a unique name, an operation description, and a set of initial labels. Roots have an empty operation. Derived nodes may refer only to earlier nodes and have no initial labels. Each output policy names a node and the labels forbidden at that output.

No actual private data belongs in a plan. Labels and descriptions are public metadata.

For every derived node and every earlier node, semantic interpretation returns one direct relationship:

| Relationship | Meaning |
| --- | --- |
| DATA | The earlier value contributes to the output value |
| CONTROL | The earlier value influences selection, execution, presence or ordering |
| BOTH | Both kinds of influence occur |
| NONE | An exhaustive declaration establishes absence of either influence |
| UNKNOWN | The declaration does not establish a supported relationship |

Positive relationships require an exact excerpt from the corresponding operation. Omission alone does not establish NONE. Hashing, aggregation and redaction do not remove influence under this model; there is no declassification operation.

## Independent interpretation

The GenLayer boundary uses a custom `run_nondet_unsafe` validator. The leader interprets the original plan. Every validator independently interprets the same plan and compares the complete ordered relationship vector, including relationships that do not change the overall outcome. Quotes may differ, but each positive quote must occur in its own operation.

An exception, invalid model response or validator disagreement must leave the audit absent. These failures must not be converted into UNKNOWN or a stored REVIEW result.

## Propagation and decisions

Deterministic code propagates labels in node order over two graphs:

- **Definite flow:** DATA, CONTROL and BOTH edges.
- **Possible flow:** definite edges plus UNKNOWN edges.

A forbidden label on a definite path produces LEAK and a concrete node path. A forbidden label reachable only through possible flow produces REVIEW and a possible path. Otherwise the output policies are CLEAR. LEAK takes precedence over REVIEW.

An immutable audit binds the owner, name, exact plan, accepted interpretation and computed report with SHA-256. A separate owner-authorized publication call is permitted only for CLEAR and the exact expected commitment. Publication does not execute the described pipeline.

## Integration

The contract interface is `audit(name, payload)`, `inspect(owner, name)`, `publish(name, expected_commitment)` and `protocol()`. Audit names are scoped to the signing address. An existing name cannot be replaced. Each owner has a maximum of twelve audits.

The deployment target is Stable Studionet, chain **61999**, RPC **https://studio.genlayer.com/api**, with full consensus and zero attached value.

## Scope of assurance

This is a specification for analysis of declarations, not a source-code analyzer, proof of program noninterference, privacy certification or enforcement gateway. Missing or misleading declarations can invalidate its practical conclusions. Independent model agreement can still be wrong. Prompts treat operation text as untrusted data, but prompt injection resistance is not an absolute guarantee.

The model is acyclic and bounded. It excludes implicit external sources, timing and resource side channels, arbitrary loops, encryption-based declassification and runtime telemetry.

## Verification requirements

A deployment claim needs the exact source digest, successful finalized deployment receipt, accepted consensus receipts and finalized state readback. Local fixture tests and schema compilation must be identified separately from live consensus.

Contract: [`0x8C09C7cc7f19a32D63Ada9012DE165c80f59B348`](https://explorer-studio.genlayer.com/address/0x8C09C7cc7f19a32D63Ada9012DE165c80f59B348). Four real transactions are FINALIZED / MAJORITY_AGREE / SUCCESS. The CLEAR audit is published; the CONTROL-leak audit retains its witness and is not published. [Network observations and limits](NETWORK.md).

Evidence summary: [evidence.json](evidence.json).

To inspect existing evidence without sending a transaction:

```sh
npm install
npm run read
```

To run the twelve scripted-host checks:

```sh
python -m unittest discover -s tests -v
```

The complete deployable source is [contracts/tracefence.py](contracts/tracefence.py). It takes no constructor arguments. An input example is [examples/public-only.json](examples/public-only.json); recorded live inputs remain in the two saved network states. Local checks are explained in [TESTING.md](TESTING.md).

SHA-256 commits exact bytes; it does not prove the semantic interpretation is objectively correct.
