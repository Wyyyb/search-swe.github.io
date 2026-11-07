# Sparse Retrieval Pruning

Speed up sparse retrieval over one million documents using **single-threaded Python on one CPU**, preserving **nDCG@10 ≥0.89 and Recall@100 ≥0.99**. Prune work without losing relevant results. After all five runs pass both quality gates, reward grows from zero at 4× reference speedup to full credit at 16×, using median complete search times.

* **Task name**: `search-swe/sparse-retrieval-pruning`
* **Domain**: `learned sparse retrieval`
* **Primary focus**: `sparse retrieval and postings pruning`
* **Primary metric**: `Quality-gated linear speedup reward`
* **Tags**: `sparse-retrieval`, `inverted-index`, `IDF`, `candidate-pruning`

## Runtime and requirements

* **Agent time budget**: up to `120 minutes`
* **Python**: `3.12`
* **Compute**: `1` CPU core, `32 GiB` memory, `80 GiB` storage
* **GPU required**: `no`
* **Network**: `no`
* **Candidate limits**: `3,600 seconds` for build and `900 seconds` for search

Implement indexing, retrieval, scoring, pruning, and ranking in Python, using
preinstalled packages such as NumPy through their normal APIs. Bash entry points
may parse arguments and launch Python. Both build and search run offline in a
single process with a single thread. Submitted native source and native
compilation are prohibited.

## Public input and output contract

### Inputs

* `/task/data/corpus.jsonl` — the full one-million-document corpus.
* `/task/data/validation/queries.jsonl` — 200 public queries.
* `/task/data/validation/qrels.tsv` — public relevance judgments.
* `/task/data/validation/stats.json` — term and document-frequency statistics.
* `/task/data/validation/reference_top100.jsonl` — public regression rankings.

### Outputs

Provide executable `/app/build.sh` and `/app/run.sh` files. The verifier runs:

~~~bash
/app/build.sh --corpus /task/data/corpus.jsonl --index-dir /path/to/index
/app/run.sh --index-dir /app/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Write one JSONL object per input query, in input order:

~~~json
{"query_id":"query-id","results":[{"doc_id":"document-id","score":0.123}]}
~~~

Return at most 100 unique corpus document IDs per query. Scores must be finite,
ordered descending, with ascending document ID as the tie-breaker.

## Evaluation

Every candidate round must reach mean NDCG@10 >=0.89 and qrels Recall@100 >=0.99 on all 1,000 hidden queries. Five rounds use fresh processes, alternating starter-first and candidate-first. Compute each system’s median complete search time; with `s=starter_median/candidate_median`:

~~~text
reward = max(0, min(1, (s - 4) / 12))
~~~

Fourfold speedup earns zero, tenfold earns 0.5, and sixteenfold or better earns one. Timing includes startup, imports, index/query loading, retrieval, output and exit. There is no warmup and OS caches are retained. Each invocation has fresh scratch; code and index are read-only, and answers cannot be reused across runs.

Candidate/reference build limits are 3,600/1,800 seconds, each search has 900 seconds and the overall verifier has 16,200 seconds. Both systems share the same one-CPU, one-thread, 32 GiB policy. Quality/output validation applies to every round. Execution, resource or required audit failure gives zero; self-reported counters are diagnostic.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/sparse-retrieval-pruning/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/sparse-retrieval-pruning/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/sparse-retrieval-pruning/task.toml)
for the complete contract at the synchronized benchmark revision.
