# Layout Page Search

Find evidence pages within a document on **one GPU**, applying query-dependent fine scoring to at most **40 pages per request**. Encoders stay frozen; an optional component is limited to five million trainable parameters and 45 minutes of training. Page-set F1 penalizes both missed evidence and extra pages; the reference quality maps to 20/100.

* **Task name**: `search-swe/layout-page-search`
* **Domain**: `document evidence pages`
* **Primary focus**: `Evidence selection under a page-scoring budget`
* **Primary metric**: `EvidencePageSetF1`
* **Tags**: `document evidence pages`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Build: 3,600 seconds. Up to 600 requests in two calls, each allowed 2,700 seconds. Encoders remain fixed; an optional component may have at most five million trainable parameters and 45 minutes of training. At most 40 pages per request may undergo query-dependent token, region or learned pairwise scoring. No external APIs or data.

## Public input and output contract

### Inputs

Page records, rendered images and extracted Markdown are in `/task/data/corpus/`; local page/vision models are in `/task/models/`. Requests provide `query_id`, `doc_id`, `question`, `domain` and `language`. Public requests and labels are under `/task/data/validation/`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return `query_id` and at most ten distinct `page_id`/finite `score` results from the specified document, in nonincreasing score order. No answer or bounding box is required.

The index remains writable across repeated query calls.

## Evaluation

For each question, compute set F1 between the returned pages and the complete
original evidence-page set. Quality is mean F1 over 515 held-out questions.
 Domain means are diagnostic.

The set metric penalizes both missing evidence and extra pages. Returning the
complete annotated evidence set achieves full per-query credit. It does not
measure answer accuracy or bounding-box localization.

### Reward mapping

For raw quality `Q`, use `b=0.5734305608092015` and `a=0.2`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 20 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

Build, query coverage, IDs, scores and stage limits must be valid. On a query-call timeout, completed valid rows still score; missing or invalid rows earn zero. Other query-command failures invalidate the call.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/layout-page-search/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/layout-page-search/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/layout-page-search/task.toml)
for the complete contract at the synchronized benchmark revision.
