# Network observations

Stable Studionet, chain 61999. Contract: `0x8C09C7cc7f19a32D63Ada9012DE165c80f59B348`.

Four transactions finalized with MAJORITY_AGREE and successful leader execution: deployment, a CLEAR audit, a LEAK audit and publication of the CLEAR commitment. All used full consensus and zero attached value. The RPC reported zero gas price. Deployed source matched the complete production file byte for byte.

The clean audit explicitly excludes reads and branches on secret. Its output has no restricted label and is published. The branch audit emits a public value only when secret is true. Its CONTROL edge propagates the restricted label to output; the result is LEAK with witness [0,2], and it is not published.

The clean and branch semantic transactions each recorded three agree votes, one disagree vote and one idle vote in the final consensus data. This is majority agreement, not unanimity. Deployment and publication recorded three agree and two idle votes. No Appeal or repeated transaction was sent.

`network/transactions.json` contains explicitly selected receipt fields and hashes of the complete captured receipts; it is not a full raw receipt export. `verification.json` binds each method and argument list to its transaction. `npm install && npm run read` fetches the existing full transactions, verifies exact deployed source, checks finality/agreement/execution and compares both saved records with finalized state. It sends no writes.

Local scripted checks: 12 passed. GitHub Actions also passed. Official genvm-linter 0.11.0 passed with only the I200 newer-runner advisory; the pinned runner compiled successfully in Stable Studio. These checks are separate from the real transactions above.

Publication rejection for LEAK, UNKNOWN propagation and model/disagreement rollback were tested locally. No additional live rejection transaction or live UNKNOWN example is claimed. Inputs are synthetic declarations; no actual private information or external program execution is involved.
