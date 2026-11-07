# Video-Moment Search

Locate a described video interval from frozen frame features on **one GPU**, with fine scoring of at most **64 intervals per request**. Raw video is unavailable; boundaries must follow the supplied time grid. Quality combines temporal overlap and threshold hits, normalized by the best grid-feasible interval; the reference quality maps to 15/100. Optional trainable components are limited to five million parameters.

* **Task name**: `search-swe/video-moment-search`
* **Domain**: `temporal video retrieval`
* **Primary focus**: `Temporal localization from fixed frame features`
* **Primary metric**: `Grid-normalized temporal-overlap utility`
* **Tags**: `temporal video retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Build: 3,600 seconds. Up to 500 requests in two calls of at most 250, each allowed 2,700 seconds. Fixed CLIP encoders; an optional temporal/scoring component may have five million trainable parameters and 45 minutes of training. Fine scoring is limited to 64 intervals per request. No external APIs.

## Public input and output contract

### Inputs

`/task/data/corpus/records.jsonl` maps videos to frozen CLIP frame features, durations and time grids. Raw videos are absent. Training examples and five validation questions include acceptable interval labels. Requests contain `query_id`, `video_id` and `description`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return `query_id`, numeric `start` and `end` in seconds: exactly one nonempty interval with both endpoints on that video’s supplied grid. Process requests independently.

The completed index is read-only during retrieval.

## Evaluation

Let x be the best IoU between the predicted interval and the original
acceptable intervals. Its utility is:

```text
u(x) = 0.7 * mean(I[x >= 0.5], I[x >= 0.7], I[x >= 0.9]) + 0.3 * x
```

Divide each query's utility by the best utility attainable with one legal
interval on its supplied grid. Average within each source, then give the two
sources equal weight.

Grid-optimal witnesses remain verifier-only. Invalid, reversed, missing,
nonfinite or non-grid intervals score zero. The grid correction accounts for
boundary precision limits; a long interval still loses IoU when it includes
unrelated time.

### Reward mapping

For raw quality `Q`, use `b=0.14696558206208937` and `a=0.15`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 15 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

The verifier checks successful index construction, executable behavior,
query IDs, finite start/end values, interval order, grid endpoints and stage
limits. Completed valid JSONL rows remain usable after a query timeout;
missing or invalid query results score zero. A non-timeout query-command failure
invalidates that call.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/video-moment-search/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/video-moment-search/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/video-moment-search/task.toml)
for the complete contract at the synchronized benchmark revision.
