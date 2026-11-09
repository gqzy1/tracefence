# TraceFence — declared information-flow audit

TraceFence gives developers a shared audit record for small data-processing plans. It catches a case that value-only checks miss: an output containing public text can still disclose a restricted fact when that fact controls whether the output is emitted.

The Intelligent Contract independently interprets every direct DATA / CONTROL / BOTH / NONE / UNKNOWN relationship. Validators rerun the interpretation from the original plan and compare the complete relationship vector. Deterministic code propagates definite and possible restriction labels, records a leak or uncertainty path, and permits publication only for a CLEAR report bound to its exact commitment.

Stable Studionet contract: `0x8C09C7cc7f19a32D63Ada9012DE165c80f59B348`.

Four finalized successful full-consensus transactions cover deployment, a CLEAR result, a CONTROL-leak result and publication of the CLEAR commitment. The semantic audit transactions reached majority agreement with dissent retained. Twelve scripted-host tests and official lint checks passed separately. [Evidence and reproduction](NETWORK.md).

The input is a public declaration of a bounded acyclic pipeline. This is not runtime monitoring, source-code analysis, privacy certification or proof of real-world noninterference. No private data, paid API, complete frontend or transfer mechanism is required.
