# Spoken-Query Document Search

Retrieve documents from noisy speech-recognition hypotheses using **one GPU**, at most **five query formulations** and **50 extra reranking pairs per request**. Recover the intended information need without audio, clean questions or a replaceable recognizer. Quality is nDCG@10 balanced across collections and noise conditions; the reference quality maps to 15/100.

* **Task name**: `search-swe/spoken-query-search`
* **Domain**: `speech uncertainty retrieval`
* **Primary focus**: `Retrieval robust to recognition errors`
* **Primary metric**: `SpokenMacroNDCG@10`
* **Tags**: `speech uncertainty retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Build: 10,800 seconds. Up to 4,600 requests in four calls of at most 1,200, each allowed 1,350 seconds. Use at most five retrieval formulations and 50 further query-document reranking pairs per request. The recognizer is fixed; follow the documented model/API allowlist.

## Public input and output contract

### Inputs

Corpus JSONL files under `/task/data/corpus/` include IDs, domain, language, title and text. Local encoder: `/task/models/encoder/`. Requests have `query_id`, `domain`, `language`, `one_best` and scored `hypotheses`, including word confidence and spans. Public requests and labels are under `/task/data/validation/`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return `query_id` and at most ten distinct `doc_id`/finite `score` results from the requested domain, in nonincreasing score order. Requests must be processed independently.

The completed index is read-only during retrieval.

## Evaluation

Compute original graded nDCG@10, average within each collection and acoustic
condition, then give the six collections and four conditions equal weight.


The split separates question families, but it is not an independently verified
speaker-disjoint benchmark. Per-condition and per-collection scores are reported
to show the effect of recognition noise.

### Reward mapping

For raw quality `Q`, use `b=0.4530094614433184` and `a=0.15`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 15 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

Build, query coverage, IDs, scores and stage limits must be valid. On a query-call timeout, completed valid rows still score; missing or invalid rows earn zero. Other query-command failures invalidate the call.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/spoken-query-search/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/spoken-query-search/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/spoken-query-search/task.toml)
for the complete contract at the synchronized benchmark revision.
