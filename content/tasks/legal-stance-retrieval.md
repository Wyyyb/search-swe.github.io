# Legal Stance Retrieval

Rank court documents supporting or refuting a requested claim, processing **311 queries in 20 seconds on one GPU**. Match the requested stance rather than topic alone. The median of all five fresh rounds, with failures ordered last, supplies the rankings; only nDCG@10 above the frozen baseline earns reward.

* **Task name**: `search-swe/legal-stance-retrieval`
* **Domain**: `legal document retrieval`
* **Primary focus**: `Claim relevance and stance matching`
* **Primary metric**: `Baseline-normalized mean NDCG@10`
* **Tags**: `stance-aware retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `16` CPUs, `32 GiB` RAM, `100 GiB` storage; one GPU
* **Build limit**: `3,600 seconds`
* **Query limit**: `20 seconds` for the entire 311-query evaluation batch

Use the supplied embedding model and documented optional API resources. Complete
model loading or start persistent services during build. The batch limit includes
startup, input loading, inference, API latency and output writing.

## Public input and output contract

### Inputs

* `/task/data/corpus.jsonl` — 3,126 court documents.
* `/task/data/examples/queries.jsonl` and `/task/data/examples/ground_truth.jsonl` — 5,318 propositions expressed as 10,636 stance-specific training inputs.
* `/task/models/Qwen3-Embedding-0.6B` — the supplied local embedding model.

The requested stance is `supported`, `refuted` or `all`; `all` accepts documents
from either stance, without requiring both. Evaluation has 311 queries. Training
examples are not mounted in the verifier.

### Outputs

Submit executable scripts and dependencies under `/app`:

~~~bash
/app/build.sh --corpus /task/data/corpus.jsonl --index-dir /app/index
/app/run.sh --index-dir /app/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl --top-k 10
~~~

The separate verifier rebuilds the index. Submission code is read-only and runs
as an unprivileged user; store writable state in the supplied index directory.

~~~json
{"query_id":"example","results":[{"doc_id":"document-id","score":0.123}]}
~~~

Each actual result list must contain exactly ten distinct known document IDs,
with finite scores in nonincreasing order. Equal scores may use any order; array
position determines rank. Produce one result for every query.

## Evaluation

Run five rounds in the same query order, rebuilding from an empty index and restarting services each time. Select the median-time batch, ordering failed, late or invalid batches last and breaking ties by round order. Compute binary document-level NDCG@10 for each question in that batch, then take their mean `Q`. Normalize only after averaging, using the exact reference:

~~~text
B = 0.5610484855098774
reward = clamp((Q - B) / (1 - B), 0, 1)
~~~

The reference must not be rounded. Relevance uses the supplied stance judgments;
the pooled labels are not an exhaustive account of all potentially useful documents.

Any failed build, fewer than three successful batches, or a failed mandatory trajectory compliance audit yields zero overall. No partial batch receives credit. Each build retains its 3,600-second limit, each batch 20 seconds, and the overall verifier allows 20,100 seconds. The single audit must have complete, consistent decisions; missing or inconsistent audit output invalidates the measurement.

The full contract is in the benchmark's [task instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/legal-stance-retrieval/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/legal-stance-retrieval/README.md),
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/legal-stance-retrieval/task.toml).
