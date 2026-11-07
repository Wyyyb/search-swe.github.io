# Incremental Vector Search

Maintain vector indexes through insertions and queries up to **K=1,000**, using **one query CPU** and at most **10% of exact-scan time**. Keep recall near perfect as each collection grows from 105,000 to 115,000 vectors, without rebuilding after every insertion batch. Reward measures logarithmic reduction in missed neighbors versus a frozen reference; speed is a gate, not a bonus.

* **Task name**: `search-swe/incremental-vector-search`
* **Domain**: `incremental vector indexes`
* **Primary focus**: `High-recall search with incremental insertions`
* **Primary metric**: `Time-gated logarithmic missed-neighbor reduction over public reference`
* **Tags**: `incremental vector indexes`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `16` CPUs, `32 GiB` RAM, `32 GiB` storage; `0` GPU(s)

Offline CPU service. Build/insertion may use 16 CPUs; each query phase is confined to one CPU. Five independent workload replays use median build, insertion and per-cell times. Each 1,000-query stage/K cell must fit 10% of its frozen exact-scan time, and its quality comes from the corresponding median-time replay. Public runtime limits set build/insertion deadlines; missing or aborted samples remain in the five-sample population. Do not rebuild the whole index after each batch.

## Public input and output contract

### Inputs

`/task/data/corpus/<dimension>/initial.npy` contains 105,000 original FP32 vectors per collection, with dimensions 1,536 and 3,072. Ten 1,000-vector insertion batches grow each to 115,000. Each stage uses 1,000 queries at K=100,200,400,800,1000. Public warmups are supplied beside the initial matrices. Under `/task/data/validation/<dimension>/`, independent development workloads contain 10,000 initial vectors, ten 100-vector insertion batches and 100 queries, with `ground_truth.npy` and `ground_truth_distances.npy` for exact Top-1000 checks. `/task/platform/limits.json` gives timing limits and the frozen reference missed counts; `/task/tools/profile_public.py` checks full-size timing and response format without exposing hidden-query recall.

### Outputs

Submit `/app/submission/run.sh` and dependencies. The verifier runs it with bash as a persistent JSONL service. `build` supplies initial vectors and writable `state_dir`; `insert` supplies a temporary vector file and consecutive IDs. Reply `{"ok":true}` only when all rows are searchable. `search` supplies `vector` and `k`; return paired `ids` and finite nonnegative L2 `distances`, at most k. Preserve original L2 semantics; internal compression is allowed. Query-dependent work and caches count in query phases.

## Evaluation

Each requested neighbor has equal weight: 25,000,000 neighbor positions per collection. Let C be missed neighbors and Cbase the frozen reference missed count. Collection value is `clip(1-log(1+C)/log(1+Cbase),0,1)`; reward averages the two collections. K=1000 contributes ten times the positions of K=100. Macro recall is diagnostic. Exact boundary ties are accepted without numerical tolerance. A failed median build/insertion or query-cell time gate, invalid execution or resource violation zeros that collection; speed within budget adds no points.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/incremental-vector-search/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/incremental-vector-search/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/incremental-vector-search/task.toml)
for the complete contract at the synchronized benchmark revision.
