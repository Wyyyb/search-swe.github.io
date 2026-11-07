# Document Page Search

Find supporting pages across multilingual reports using **one GPU**, with **2,700 seconds per batch of up to 7,250 requests**. Search an entire domain without a target document ID, combining text, charts and tables. Quality is nDCG@10 averaged equally across eight domains; the reference quality maps to 20/100 and perfect quality to 100.

* **Task name**: `search-swe/document-page-search`
* **Domain**: `multilingual page retrieval`
* **Primary focus**: `Cross-document multilingual page ranking`
* **Primary metric**: `DomainMacroNDCG@10`
* **Tags**: `multilingual page retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Build: 10,800 seconds. Up to 14,500 requests in two calls of at most 7,250; each call has 2,700 seconds. Supplied page and vision encoders and the documented API allowlist are available.

## Public input and output contract

### Inputs

`/task/data/corpus/records.jsonl` supplies page IDs, domains, document IDs, image paths and Markdown transcriptions. Models are under `/task/models/page-encoder/` and `/task/models/vision-backbone/`. Requests contain `query_id`, `question`, `domain` and `language`. Public requests and labels are under `/task/data/validation/`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return `query_id` and at most ten distinct `page_id`/finite `score` results in nonincreasing score order, all from the requested domain. Search the whole domain, without a supplied target document. No answer or bounding box is required.

The index remains writable across repeated query calls.

## Evaluation

Compute nDCG@10 with the original graded relevance labels and linear gains.
Average query scores within each domain, then give the eight domains equal
weight. Missing or invalid query results remain in the denominator.

### Reward mapping

For raw quality `Q`, use `b=0.5362634643282924` and `a=0.2`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 20 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

Build, query coverage, IDs, scores and stage limits must be valid. On a query-call timeout, completed valid rows still score; missing or invalid rows earn zero. Other query-command failures invalidate the call.

The integrity audit runs independently three times. Its reported value is the mean of the three binary decisions; all three must accept for a positive task reward. Missing, failed or malformed audit evidence invalidates the measurement.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/document-page-search/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/document-page-search/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/document-page-search/task.toml)
for the complete contract at the synchronized benchmark revision.
