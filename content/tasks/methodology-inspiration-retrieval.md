# Methodology Inspiration Retrieval

Find three papers whose methods address a proposed research problem, processing **122 queries in 12 seconds on one GPU**. Retrieve transferable methods rather than merely similar topics, using the supplied Stella encoder and permitted resources. Reward is Recall@3 gain above 0.310109, normalized to the attainable top-three ceiling; the whole batch must finish on time.

* **Task name**: `search-swe/methodology-inspiration-retrieval`
* **Domain**: `research-method retrieval`
* **Primary focus**: `Method transfer beyond topical similarity`
* **Primary metric**: `Mean Recall@3 improvement`
* **Tags**: `research-method retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `16` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Build: 1,200 seconds including resident-service initialization. The entire hidden batch has 12 seconds including APIs and output. One GPU and the supplied Stella encoder; only documented external resources may be used.

## Public input and output contract

### Inputs

`/task/data/corpus.jsonl`, labeled `/task/data/examples.jsonl` and `/task/models/stella_en_400M_v5`. Query rows contain `query_id` and `text`; examples are not mounted in verification.

### Outputs

Submit executable `/app/build.sh --corpus PATH --index-dir DIR` and `/app/run.sh --index-dir DIR --queries PATH --output PATH --top-k 3`, with dependencies under `/app`. Code is read-only during verification; generated state belongs in the supplied index.

Return one row per query with `query_id`, `results`, and at most three distinct corpus `doc_id`/finite `score` pairs in descending score order, ties by corpus order. Empty results are valid.

## Evaluation

Q is mean Recall@3 across 122 held-out queries. Reward is `clip((Q-B)/(U-B),0,1)` with exactly `B=0.310109` and attainable Top-3 ceiling `U=0.9901639344262295`. Baseline rounding is intentional. The ceiling accounts for queries with more than three positives; standard macro recall is preserved. Build failure, invalid output or whole-batch timeout yields zero.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/methodology-inspiration-retrieval/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/methodology-inspiration-retrieval/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/methodology-inspiration-retrieval/task.toml)
for the complete contract at the synchronized benchmark revision.
