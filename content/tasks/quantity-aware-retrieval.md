# Quantity-aware Retrieval

Rank clinical passages satisfying numerical conditions in **five seconds per query on one GPU**, using the supplied model and examples. Resolve quantities, units and inequalities across 153,252 passages; the training examples are edited text, not corpus-ID labels. Reward is mean nDCG@10 improvement above 0.1847, normalized so perfect retrieval earns full credit.

* **Task name**: `search-swe/quantity-aware-retrieval`
* **Domain**: `clinical passage retrieval`
* **Primary focus**: `Quantity-sensitive semantic retrieval`
* **Primary metric**: `Baseline-normalized mean nDCG@10`
* **Tags**: `numerical constraints`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `16` CPUs, `32 GiB` RAM, `100 GiB` storage; one GPU
* **Build limit**: `1,200 seconds`
* **Query limit**: `5 seconds` per question, evaluated sequentially

Use only the supplied data/model and documented optional OpenRouter/Jina resources.
Additional datasets, weights and external answer lookup are prohibited. The query
limit includes startup, inference, API work and output writing.

## Public input and output contract

### Inputs

* `/task/data/corpus.jsonl` — 153,252 MedQuant passages.
* `/task/data/examples.jsonl` — 80,000 examples spanning 12,453 distinct query texts.
* `/task/models/Qwen3-Embedding-0.6B` — the supplied local embedding model.

The examples contain synthetically edited passage text; they are not corpus-ID
relevance judgments. There is no public retrieval validation split. The verifier
withholds training examples and evaluates 209 retained queries after removing one query with invalid positive labels.

### Outputs

Submit executable scripts and dependencies under `/app`:

~~~bash
/app/build.sh --corpus /task/data/corpus.jsonl --index-dir /app/index
/app/run.sh --index-dir /app/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl --top-k 10
~~~

The verifier rebuilds once, then runs each query separately as an unprivileged
user with read-only submission code. Put writable runtime state in the supplied
index directory; build may initialize a persistent service.

~~~json
{"query_id":"example","results":[{"doc_id":"document-id","score":0.123}]}
~~~

Return zero to ten distinct known IDs with finite descending scores and ties
in corpus order. Empty results are valid and score zero.

## Evaluation

Let `Q` be mean binary nDCG@10 over all 209 questions. Use the specified reference
constant exactly as given:

~~~text
B = 0.1847
reward = clamp((Q - B) / (1 - B), 0, 1)
~~~

The rounded constant `0.1847` is the contract's baseline; do not substitute an
unrounded historical measurement. There is no independent timing bonus.

A timed-out question contributes zero without leaving the denominator. Other
execution/output failures, failed build, integrity violations or a failed
mandatory trajectory audit set the overall reward to zero.

The full contract is in the benchmark's [task instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/quantity-aware-retrieval/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/quantity-aware-retrieval/README.md),
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/quantity-aware-retrieval/task.toml).
