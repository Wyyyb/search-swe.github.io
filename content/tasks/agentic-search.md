# Agentic Search

Find five documents answering a multi-constraint question over 100,195 documents, with at most **20 search actions** on a CPU-only host. Improve the supplied ReAct/BM25 starter to cover all required evidence within a 600-second index build and shared query budget. Reward is the fraction of gold documents recovered, averaged over 20 questions.

* **Task name**: `search-swe/agentic-search`
* **Domain**: `multi-constraint search`
* **Primary focus**: `agentic retrieval and document coverage`
* **Primary metric**: `Gold Recall@5`
* **Tags**: `BrowseComp-Plus`, `multi-constraint-retrieval`, `ReAct`, `agentic-search`, `BM25`

## Runtime and requirements

* **Agent time budget**: up to `120 minutes`
* **Python**: `3.12`
* **Compute**: `32` CPU cores, `16 GiB` memory, `200 GiB` storage
* **GPU required**: `no`
* **Network**: `restricted` — allowlisted OpenRouter and Jina resources only
* **Build limit**: `600 seconds`
* **Retrieval-round limit**: at most `20` search actions per query
* **Verifier execution**: one shared `15,300-second` budget includes build and scoring; hidden queries run up to five concurrently and have no individual timeout

## Public input and output contract

### Inputs

* `/task/data/corpus.jsonl` — the 100,195-document BrowseComp-Plus corpus.
* `/task/data/validation/queries.jsonl` — 20 public development questions.
* `/task/data/validation/qrels_gold.txt` — public gold document relevance labels.
* `/app/starter` — an editable ReAct loop backed by a SQLite FTS5/BM25 search service.

### Outputs

The submission must provide executable `build.sh` and `run.sh` entry points under `/app`. Each query produces one JSONL object with its `query_id` and exactly five distinct valid corpus IDs in `doc_ids`.

## Evaluation

The hidden split contains 20 held-out questions with private gold document labels. For each query, Gold Recall@5 is the fraction of its gold documents returned in the five selected IDs. Reward is the mean across hidden queries:

```text
GoldRecall@5(q) = |returned IDs intersect gold IDs| / |gold IDs|
reward = mean(GoldRecall@5)
score = 100 * reward
```

Execution and output validation are hard gates. Retrieval quality is deterministic; the separate audit checks resource, retrieval-round and integrity constraints. The complete verifier allows 20,000 seconds, including auditing.

The integrity audit runs independently three times. Its reported value is the mean of the three binary decisions; all three must accept for a positive task reward. Missing, failed or malformed audit evidence invalidates the measurement.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/agentic-search/instruction.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/agentic-search/task.toml)
for the complete contract at the reviewed benchmark revision.
