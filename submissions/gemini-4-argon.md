# Community submission: gemini-4-argon (Antigravity CLI harness)

**Equal-weight mean: 21.80 / 100** over all 47 Search-SWE tasks (26 tasks scored 0, 4 perfect 100s).

- **Model:** gemini-4-argon, reasoning effort `high` (the Antigravity CLI harness rejects `max`; `high` is its top setting).
- **Harness:** Antigravity CLI (`agy`) native agent route, Vertex AI via Application Default Credentials. This is **not** the Codex harness behind the leaderboard, nor the Claude Code harness of the companion claude-sonnet-5-5 submission, so cross-harness comparison is confounded.
- **Pipeline:** official `search-swe` CLI → Harbor native route with the separate per-task verifier; score = native reward × 100, equal task weight.
- **Hardware:** single node, 8× NVIDIA H100 80GB HBM3, 208 vCPU, 1842 GiB RAM, driver 570.195.03, Docker 29.9.3.

## Trajectories
46 of 47 complete ATIF trajectories and verifier rewards (credentials redacted, host paths aliased):
<https://huggingface.co/datasets/ubowang/search-swe-gemini-4-argon>

## Notes
- Lower than the companion claude-sonnet-5-5 run (30.66), and the gap is largely genuine: on several tasks argon submitted incomplete deliverables (e.g. `same-place-image-search` produced only `features.py` with no build/run scripts; several submissions did not run), and it terminated earlier (trajectories ~38 MB vs ~477 MB for sonnet). The integrity audit (`jailbreak_judge`) is mostly **not** the cause — on `same-place-image-search` the audit explicitly passed, and `sparse-retrieval-pruning` scored 100 despite a non-fatal judge-environment warning.
- `large-scale-formula-retrieval` did not complete (a `/sys/fs/cgroup/memory.events` cgroup limit in the bounded-storage task); counted as 0, as for the sonnet run. `incremental-vector-search` needed a root rerun (100).
- Integrating into the live board needs the same importer support for a non-Codex harness as noted in the sonnet submission.
