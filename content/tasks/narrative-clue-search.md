# Narrative-Clue Search

Identify a remembered work from scattered, uncertain clues on **8 CPUs**, with **2,700 seconds per batch of up to 225 descriptions**. Resolve long narratives whose details may be incomplete or mistaken. Quality is mean nDCG@10 over 445 questions, giving each question equal weight; the reference quality maps to 20/100.

* **Task name**: `search-swe/narrative-clue-search`
* **Domain**: `narrative retrieval`
* **Primary focus**: `Retrieval from incomplete and uncertain recollections`
* **Primary metric**: `QueryMeanNDCG@10`
* **Tags**: `narrative retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `0` GPU(s)

Build: 3,600 seconds. Up to 450 requests in two calls of at most 225; each call has 2,700 seconds. Only the documented OpenRouter/Jina APIs may supplement local computation.

## Public input and output contract

### Inputs

`/task/data/corpus/records.jsonl` contains `doc_id`, `title` and article `text`. Queries contain `query_id` and `question`. Public sentence annotations also appear in `/task/data/training/sentence_labels.jsonl`. Public requests and labels are under `/task/data/validation/`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return `query_id` and at most ten distinct `doc_id`/finite `score` results, ordered by nonincreasing score.

The index remains writable across repeated query calls.

## Evaluation

Compute nDCG@10 using complete original qrels, then average equally over
445 held-out questions.

Four category means based on original human uncertainty annotations and a fixed
median narrative length are diagnostics. They do not change query weights or
introduce model-generated categories.

### Reward mapping

For raw quality `Q`, use `b=0.40178618363049623` and `a=0.2`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 20 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

Build, query coverage, IDs, scores and stage limits must be valid. On a query-call timeout, completed valid rows still score; missing or invalid rows earn zero. Other query-command failures invalidate the call.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/narrative-clue-search/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/narrative-clue-search/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/narrative-clue-search/task.toml)
for the complete contract at the synchronized benchmark revision.
