# Visual-Document Question Answering

Answer questions from long PDFs, charts and tables **without a GPU**, with **10,800 seconds per batch of up to 1,250 requests**. Use permitted APIs to reason across pages, handle numbers and recognize unanswerable questions. Quality averages three answer judgments with equal source weight; the reference maps to 20/100. Supporting pages are required output, but citation overlap is diagnostic.

* **Task name**: `search-swe/visual-document-qa`
* **Domain**: `visual document QA`
* **Primary focus**: `Cross-page reasoning and answerability`
* **Primary metric**: `Answer accuracy, equally weighted across sources`
* **Tags**: `visual document QA`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `0` GPU(s)

Build: 14,400 seconds. Up to 2,500 requests in two calls of at most 1,250, each allowed 10,800 seconds. No GPU; only documented external resources are permitted.

### Host configuration

Set `VERIFIER_OPENAI_API_KEY` to an OpenRouter key allowing
`deepseek/deepseek-v4.1-flash` for trajectory auditing and `deepseek/deepseek-v4.1-flash-1017`
for the fixed document-answer judge. Configure submission services separately
using the [submission-key guide](https://github.com/VectorSpaceLab/Search-SWE/blob/main/docs/evaluation/submission-models.md).

## Public input and output contract

### Inputs

`/task/data/corpus/records.jsonl` maps documents to original PDFs, extracted page text and page counts. Requests have `query_id`, `doc_id` and `question`; PDFs may be rendered directly. Public requests and labels are under `/task/data/validation/`.

### Outputs

Submit executable `/app/build.sh` and `/app/run.sh` and all supporting files under `/app`. The fresh verifier rebuilds the index and runs commands as a non-root user with code and inputs read-only. Honor the supplied index, output, `TMPDIR` and cache paths; the index parent is not writable.

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /work/index
/app/run.sh --index-dir /work/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Return `query_id`, a nonempty `answer` string and supporting `pages`: distinct integers from 1 through the document’s `page_count`. Invalid page lists invalidate that query’s output. Give the final answer and units directly; say when information is absent, using an empty page list when no evidence exists.

The index remains writable across repeated query calls.

## Evaluation

MMLongBench-Doc integer and float answers use the source answer-extraction
prompt and numeric comparators. Text, list and unanswerable answers use a
binary semantic judgment of the question, reference and full submitted answer.
Equivalent wording receives credit; incorrect entities or comparisons, missing
list items and unsupported claims do not. Each semantic judgment records a reason.
FinRAGBench-V retains its original binary answer judge. Trusted model calls use
`deepseek/deepseek-v4.1-flash-1017` through OpenRouter.

Hold each submitted answer fixed and run its source-specific evaluation three times, including LLM extraction for numeric answers. Apply the numeric comparator to each extraction and average the three decisions arithmetically; semantic and FinRAG judgments use the same averaging. Then average answers within each source and give the two sources equal weight. Any failed trusted call invalidates the measurement. The overall verifier allows 59,400 seconds.

Evidence-page precision, recall and F1 are computed once as diagnostics, not part of the primary answer score. Page-list validity remains an output requirement.

### Reward mapping

For raw quality `Q`, use `b=0.4350989780543772` and `a=0.2`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 20 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

The verifier checks execution, output structure, document/page validity and
stage limits. Completed valid rows survive query-call timeout; missing or invalid
rows receive zero. Other query-command failures invalidate that call.
Trusted answer-extraction or judge transport failures invalidate the measurement
rather than establishing a low baseline or model score.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/visual-document-qa/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/visual-document-qa/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/visual-document-qa/task.toml)
for the complete contract at the synchronized benchmark revision.
