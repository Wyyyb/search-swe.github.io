# Sketch-and-Text Image Search

Retrieve artwork from a partial sketch and scene description using frozen CLIP on **one GPU**, with at most **30 minutes of fusion adaptation**. Combine incomplete visual cues with text of varying detail. Quality balances top-three recall and reciprocal rank across three description levels; the reference quality maps to 15/100.

* **Task name**: `search-swe/sketch-text-search`
* **Domain**: `sketch and text retrieval`
* **Primary focus**: `Partial-sketch and text fusion`
* **Primary metric**: `LevelMacroRecallMRR@3`
* **Tags**: `sketch and text retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Build: 3,600 seconds. Up to 1,260 requests in three calls of at most 420, each allowed 1,800 seconds. CLIP encoders remain fixed; scoring/fusion adaptation may use at most 30 minutes. Use supplied local resources only.

## Public input and output contract

### Inputs

Gallery records/images are under `/task/data/corpus/`, CLIP under `/task/models/clip/`, and training/validation query-label pairs under `/task/data/training/` and `/task/data/validation/`. Requests contain `query_id`, `description` and absolute `sketch_path`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return `query_id` and at most ten distinct `image_id`/finite `score` results in nonincreasing score order. Process each pair independently; other requests are not context. Only the first three ranks affect quality.

The completed index is read-only during retrieval.

## Evaluation

Per-query quality is `0.5 × Recall@3 + 0.5 × MRR@3`.
Average within each of the three description levels, then give the levels
equal weight.

Up to ten results are accepted by the interface, but only the first three
affect the metric. The composite and partial-sketch input are task adaptations;
they do not reproduce the source paper's reported scores.

### Reward mapping

For raw quality `Q`, use `b=0.32306763285024154` and `a=0.15`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 15 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

Build, query coverage, IDs, scores and stage limits must be valid. On a query-call timeout, completed valid rows still score; missing or invalid rows earn zero. Other query-command failures invalidate the call.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/sketch-text-search/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/sketch-text-search/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/sketch-text-search/task.toml)
for the complete contract at the synchronized benchmark revision.
