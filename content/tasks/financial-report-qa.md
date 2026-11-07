# Financial-Report Evidence Retrieval

Find evidence across 885 financial reports on **8 CPUs**, returning at most **five spans of 512 characters each** per question. No target report is given. Returned text must fully cover required facts, including table context; partial overlap does not count. Mean evidence recall determines quality, with the reference mapped to 20/100. Generating a financial answer is not required.

* **Task name**: `search-swe/financial-report-qa`
* **Domain**: `financial evidence retrieval`
* **Primary focus**: `Complete evidence coverage with short text spans`
* **Primary metric**: `EvidenceRecall@5`
* **Tags**: `financial evidence retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `0` GPU(s)

Build: 1,800 seconds. Up to 8,000 requests in two calls of at most 4,000, each allowed 3,600 seconds. Only documented OpenRouter/Jina resources are available; no GPU.

## Public input and output contract

### Inputs

`/task/data/corpus/reports.jsonl` contains all 885 reports with `document_id` and full `text`. Queries have `query_id` and `question`, without a target report ID. Public requests and labels are under `/task/data/validation/`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return exactly `query_id` and `spans`. Supply at most five ranked objects containing exactly `document_id`, `start`, `end`. Offsets count original Unicode characters, with inclusive start and exclusive end; each nonempty span is at most 512 characters. Empty results are permitted.

The index remains writable across repeated query calls.

## Evaluation

For each question, EvidenceRecall@5 is the number of covered reference
evidence units divided by the number of required units. Average these recalls
equally over the 4,236 held-out questions.

A fact is covered when the union of returned spans in the correct report
completely covers at least one verified location for that fact. Partial overlap
is insufficient. Multiple hits on the same fact do not add credit. Several
facts can fit in one span, and adjacent spans can jointly cover a fact.

Evidence locations are aligned to complete FinQA support text and table
context, with checks on numeric values and formatting. They are not inferred
by searching for the expected final answer number.

### Reward mapping

For raw quality `Q`, use `b=0.6831800740440966` and `a=0.2`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 20 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

The verifier checks successful index construction, executable behavior,
query IDs, span count, report IDs, Unicode offsets and the 512-character limit.
Duplicate output rows invalidate their query. Repeated evidence spans do not
increase recall. Completed valid JSONL rows remain usable after a query timeout;
missing or invalid query results score zero. A non-timeout query-command failure
invalidates that call.

The integrity audit runs independently three times. Its reported value is the mean of the three binary decisions; all three must accept for a positive task reward. Missing, failed or malformed audit evidence invalidates the measurement.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/financial-report-qa/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/financial-report-qa/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/financial-report-qa/task.toml)
for the complete contract at the synchronized benchmark revision.
