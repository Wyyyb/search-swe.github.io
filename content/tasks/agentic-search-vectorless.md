# Agentic Search — Vectorless

Find five documents in a 100,195-document corpus using **neither embeddings nor BM25**, with at most **20 search actions** per question. Build CPU-only retrieval from scratch in 600 seconds; permitted generation can guide search, but external retrieval and reranking are unavailable. Reward is mean gold-document recall, so finding only one part of a multi-constraint question leaves credit behind.

* **Task name**: `search-swe/agentic-search-vectorless`
* **Domain**: `multi-step document retrieval`
* **Primary focus**: `Embedding-free and BM25-free search`
* **Primary metric**: `GoldRecall@5`
* **Tags**: `vectorless search`, `search-swe`

## Runtime and requirements

* **Agent budget**: `120 minutes`
* **Compute**: `32` CPUs, `16 GiB` RAM, `200 GiB` storage; no GPU
* **Build limit**: `600 seconds`
* **Shared execution budget**: `15,300 seconds`, including build, queries and scoring
* **Verifier budget**: `27,000 seconds`, including the compliance audit

No embeddings or BM25 variants are allowed during indexing or search. External
retrieval and reranking services are prohibited. Only the generation resources
listed in `/task/docs/available_resources.md` may be called through OpenRouter.
Each query may use at most 20 retrieval rounds; independently executed searches
count separately even when batched. Up to five query invocations share the index
concurrently, with no separate per-query timeout.

## Public input and output contract

### Inputs

* `/task/data/corpus.jsonl` — 100,195 documents, identified by `docid`.
* `/task/data/validation/queries.jsonl` — 20 public questions with `query_id` and `question`.
* `/task/data/validation/qrels_gold.txt` — public relevance judgments in TREC format.

There is no supplied search starter or index. The 20 evaluation questions and
their gold document IDs are disjoint from the public examples.

### Outputs

Submit executable entry points and dependencies under `/app`:

~~~bash
/app/build.sh --corpus /task/data/corpus.jsonl --index-dir /app/index
/app/run.sh --index-dir /app/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

The fresh verifier transfers `/app` and rebuilds the index. Submission commands
run without grading privileges; global development installations and running
processes do not transfer. Honor the supplied paths and support concurrent queries.

~~~json
{"query_id":"example-1","doc_ids":["100","101","102","103","104"]}
~~~

Return exactly five distinct, nonempty, known document IDs as strings and exactly
one result for every input query.

## Evaluation

For each query, GoldRecall@5 is the fraction of its gold documents present in
the returned five. Reward is the mean across all 20 evaluation queries, on a
0–1 scale. There is no separate latency or index-size bonus.

Execution failures or invalid output yield zero overall. The audit checks resource limits, retrieval rounds and submission integrity.

The integrity audit runs independently three times. Its reported value is the mean of the three binary decisions; all three must accept for a positive task reward. Missing, failed or malformed audit evidence invalidates the measurement.

The full contract is in the benchmark's [task instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/agentic-search-vectorless/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/agentic-search-vectorless/README.md),
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/agentic-search-vectorless/task.toml).
