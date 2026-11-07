# Composed Image Search

Retrieve photographs matching an image plus a requested change, using **one GPU** and at most **100 additional candidate-image inspections per request**. Preserve the reference image’s relevant content while applying the modification. Quality combines CIRCO average precision and CIRR recall with equal source weight; the reference quality maps to 20/100 and perfect quality to 100.

* **Task name**: `search-swe/composed-image-search`
* **Domain**: `composed image retrieval`
* **Primary focus**: `Reference-image and modification-text composition`
* **Primary metric**: `Equal-source mean of CIRCO average precision and CIRR recall`
* **Tags**: `composed image retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Build: 3,600 seconds. Up to 4,400 requests in two calls of at most 2,200, each allowed 14,400 seconds. Additional query-dependent visual inspection is limited to 100 candidate images per request. Use the supplied CLIP and only documented API resources.

## Public input and output contract

### Inputs

`/task/data/corpus/records.jsonl` maps image IDs to gallery paths. Local CLIP weights are at `/task/models/clip/`. Requests contain `query_id`, `reference_image_id`, `modification` and optional-content `shared_concept`. Public requests and labels are under `/task/data/validation/`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return `query_id` and `results`, containing at most 50 distinct `image_id`/finite `score` pairs in nonincreasing score order. Exclude the reference image.

The index remains writable across repeated query calls.

## Evaluation

For CIRCO, quality is the mean of AP@5, AP@10, AP@25 and AP@50.
For CIRR, it is the mean of Recall@1, Recall@5, Recall@10 and Recall@50.
Queries are averaged within each source, then the two source scores receive
equal weight.

The source metrics retain their original positive labels. The shared gallery
and equal weighting of the two sources are this task's adaptation; unlabeled
alternatives are not treated as newly certified negatives.

### Reward mapping

For raw quality `Q`, use `b=0.26812065144613684` and `a=0.2`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 20 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

Build, query coverage, IDs, scores and stage limits must be valid. On a query-call timeout, completed valid rows still score; missing or invalid rows earn zero. Other query-command failures invalidate the call.

The integrity audit runs independently three times. Its reported value is the mean of the three binary decisions; all three must accept for a positive task reward. Missing, failed or malformed audit evidence invalidates the measurement.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/composed-image-search/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/composed-image-search/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/composed-image-search/task.toml)
for the complete contract at the synchronized benchmark revision.
