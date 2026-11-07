# Same-Place Image Search

Find photos of the same physical place using frozen CLIP on **one GPU**, with geometric verification of at most **20 candidates per request**. Handle viewpoint changes, scale and occlusion among the source benchmark’s Hard positives. Quality is top-five nDCG averaged equally across Oxford and Paris; the reference quality maps to 15/100.

* **Task name**: `search-swe/same-place-image-search`
* **Domain**: `landmark retrieval`
* **Primary focus**: `Place recognition under viewpoint changes`
* **Primary metric**: `HardPlaceMacroNDCG@5`
* **Tags**: `landmark retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Build: 3,600 seconds. Up to 140 requests in two calls of at most 70, each allowed 2,700 seconds. Keep the supplied CLIP encoder fixed. Additional pixel-based geometric verification may inspect at most 20 candidates per request. No external APIs.

## Public input and output contract

### Inputs

Gallery images and `records.jsonl` are under `/task/data/corpus/`; CLIP is under `/task/models/clip/`. Requests contain `query_id`, absolute query `image_path` and `exclude_image_ids`. Public requests and labels are under `/task/data/validation/`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return `query_id` and at most five distinct eligible `image_id`/finite `score` pairs in nonincreasing order. Respect every exclusion and process requests independently.

The completed index is read-only during retrieval.

## Evaluation

Compute binary nDCG@5 against the original Hard positives after removing
excluded images. Original Easy and Junk images appear in `exclude_image_ids` and are not treated as negatives. Average within Oxford and Paris, then give the two sources
equal weight.

This task uses the source Hard relevance protocol with a task-specific top-five
metric. Invalid or excluded returned IDs invalidate that query.

### Reward mapping

For raw quality `Q`, use `b=0.5364309790092764` and `a=0.15`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 15 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

Build, query coverage, IDs, scores and stage limits must be valid. On a query-call timeout, completed valid rows still score; missing or invalid rows earn zero. Other query-command failures invalidate the call.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/same-place-image-search/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/same-place-image-search/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/same-place-image-search/task.toml)
for the complete contract at the synchronized benchmark revision.
