# Long-PDF Sentence Evidence

Find up to **five original supporting sentences** in a 2,043-page novel within **30 seconds per query**, using CPU-only retrieval and permitted APIs. Evidence must jointly establish the requested interpretation, including comparisons and causal links. Quality averages three semantic-support judgments per question; any valid original sentence set can earn credit if it fully supports the interpretation.

* **Task name**: `search-swe/long-pdf-evidence`
* **Domain**: `in-document evidence retrieval`
* **Primary focus**: `Jointly sufficient original-sentence evidence`
* **Primary metric**: `SentenceEvidenceAccuracy`
* **Tags**: `in-document evidence retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `16` CPUs, `16 GiB` RAM, `100 GiB` storage; `0` GPU(s)

Build: 2,400 seconds, including starting the retrieval service. Each query invocation: 30 seconds, with up to five concurrent invocations and a shared 1,800-second query phase. CPU-only; documented OpenRouter/Jina resources are permitted. Only `/app` transfers; code runs unprivileged in a fresh verifier with supplied writable index and output paths.

## Public input and output contract

### Inputs

`/task/data/corpus` contains the 2,043-page War and Peace PDF and fixed inventory of 28,798 sentence units. Ten public queries and sufficient reference evidence are under `/task/data/validation/`. Twelve evaluation questions are held out.

### Outputs

Provide executable `/app/build.sh` and `/app/run.sh` with dependencies:

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /path/to/index
/app/run.sh --index-dir /path/to/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl --top-k 5
~~~

Build saves all runtime artifacts and starts a service ready for repeated query calls. Return exactly `query_id` and `results`, containing zero to five distinct objects with exactly `sentence_id` and `sentence`. Copy whole inventory units, with only NFKC/whitespace normalization tolerated. Combined text is at most 16,000 characters. Do not return page rankings, generated answers or paraphrases.

## Evaluation

Evidence is judged for semantic support, not matching reference wording or sentence IDs. Equivalent explanations and harmless redundancy are accepted, while requested comparisons, qualifications and causal links must still be supported. Material contradictions or unresolved essential referents prevent complete-support credit.

Each fixed retrieved evidence set is judged independently three times. SentenceEvidenceAccuracy averages the three binary support decisions per question, then averages all twelve questions equally; retrieval runs once. Incomplete, empty, malformed, failed or timed-out results zero their query. Shared build/setup or audit failure zeros the task. Reward equals accuracy on a 0–1 scale; judge service failures invalidate the measurement rather than measure retrieval quality.

Configure the verifier-only `ANSWER_JUDGE_MODEL_NAME`, `ANSWER_JUDGE_BASE_URL` and `ANSWER_JUDGE_API_KEY`; the endpoint must satisfy the task’s verifier network policy. Evidence judging has a 5,400-second budget within the 14,400-second verifier.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/long-pdf-evidence/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/long-pdf-evidence/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/long-pdf-evidence/task.toml)
for the complete contract at the synchronized benchmark revision.
