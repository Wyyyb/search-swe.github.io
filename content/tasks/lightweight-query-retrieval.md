# Lightweight Query Retrieval

Retrieve for **1,271 queries in under 0.8 seconds median batch time** on one GPU, while retaining **macro nDCG@10 of at least 0.45**. Build once and serve five fresh runs with the supplied local model. Every run must pass the quality gate; reward then increases linearly as median batch time approaches zero. Build, loading and warmup are outside this timer.

* **Task name**: `search-swe/lightweight-query-retrieval`
* **Domain**: `latency-constrained retrieval`
* **Primary focus**: `Batch latency reduction after a quality gate`
* **Primary metric**: `Retrieval runtime after a macro nDCG@10 quality gate`
* **Tags**: `latency-constrained retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `16` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Offline, one GPU with supplied Llama-3.2-1B. Build: 1,200 seconds; service load: 120 seconds; public warmup: 60 seconds. Each complete hidden batch has a 120-second hard limit. The index is built once and five fresh service runs are measured.

## Public input and output contract

### Inputs

`/task/data/corpus.jsonl`, labeled `/task/data/examples.jsonl`, and `/task/models/Llama-3.2-1B`. Examples are absent in verification. Evaluation has 1,271 queries across three collections.

### Outputs

Submit `/app/build.sh --corpus PATH --index-dir DIR` and `/app/run.sh --index-dir DIR --serve` under `/app`. Index becomes read-only; use supplied temporary storage during serving. Emit `{"status":"ready"}` after loading.

Each stdin request contains `queries` with `query_id`, `collection`, `text`, `instruction`, plus `top_k:10`. Return a `results` array covering every query exactly once, each with at most ten unique collection-valid `doc_id`/finite descending `score` results. Flush one JSON response per request.

## Evaluation

Every run must reach collection-macro linear-gain nDCG@10 >=0.45. Let T be median complete-batch retrieval seconds across five fresh runs, excluding build/load/warmup. Reward is `clip((0.8-T)/0.8,0,1)` after all gates. At or above 0.8 seconds reward is zero; full credit is the theoretical zero-runtime limit, not a positive-time plateau. Invalid output, execution or resource failures zero the task.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/lightweight-query-retrieval/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/lightweight-query-retrieval/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/lightweight-query-retrieval/task.toml)
for the complete contract at the synchronized benchmark revision.
