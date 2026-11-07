# Scientific-Paper Question Answering

Answer questions over **300 research-paper PDFs** on **16 CPUs and 16 GiB RAM**, with **900 seconds per question** and permitted APIs. Retrieve the correct supporting paper and produce a semantically correct answer; either alone is insufficient. Each fixed answer receives three judgments, averaged across ten questions, but a mismatched evidence document earns zero.

* **Task name**: `search-swe/scientific-paper-qa`
* **Domain**: `scientific question answering`
* **Primary focus**: `evidence-grounded RAG over PDFs`
* **Primary metric**: `LLMJudgeAccuracy`
* **Tags**: `PDF`, `RAG`, `scientific-documents`, `question-answering`, `evidence-attribution`

## Runtime and requirements

* **Agent time budget**: up to `120 minutes`
* **Python**: `3.12`
* **Compute**: `16` CPU cores, `16 GiB` memory, `100 GiB` storage
* **GPU required**: `no`
* **Network**: `restricted` — allowlisted OpenRouter and Jina resources only
* **Build limit**: `3,600 seconds`
* **Per-query limit**: `900 seconds`, with up to five query processes running concurrently

## Public input and output contract

### Inputs

* `/task/data/corpus` — 300 research-paper PDFs.
* `/task/data/validation/queries.jsonl` — 10 public development questions.
* `/task/data/validation/golden_answers.jsonl` — public reference answers and supporting document IDs.

### Outputs

The submission must provide executable `build.sh` and `run.sh` entry points under `/app`. Each query produces exactly one JSONL object containing its `query_id`, an `answer` containing non-whitespace text and at most 20,000 characters after JSON decoding, and one corpus document ID in `evidence` (the PDF filename without `.pdf`).

The index and any shared service must support up to five concurrent hidden-query invocations. Each per-query output and the combined results must be regular files of at most 64 MiB; exceeding an answer or output limit invalidates the submission.

## Evaluation

The hidden split contains 10 held-out questions over the same PDF corpus. A question earns credit only when its evidence document matches the reference. Its fixed answer is then judged independently three times for semantic equivalence, and the three binary decisions are averaged. `LLMJudgeAccuracy` averages these query values equally. Retrieval and answer generation run once; a failed or malformed judge call invalidates the measurement rather than reducing the number of decisions:

```text
query_score = evidence_match * mean(three_answer_judgments)
reward = LLMJudgeAccuracy = mean(query_score)
score = 100 * reward
```

Failed execution or structurally invalid output makes the entire submission invalid. A separate trajectory audit checks task and resource compliance and sets the final reward to `0` if it fails. Submission API access, answer-judge credentials, and trajectory-audit credentials are separate security domains.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/scientific-paper-qa/instruction.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/scientific-paper-qa/task.toml)
for the complete contract at the reviewed benchmark revision.
