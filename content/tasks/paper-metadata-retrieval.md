# Paper Metadata Retrieval

Find the single matching paper among 70,000 records in **30 seconds on 16 CPUs**, without training or external search. Satisfy both the research need and metadata conditions: submission dates differ from publication dates, and institution location differs from citizenship. Reward is exact top-one accuracy; a plausible paper that violates a condition earns nothing.

* **Task name**: `search-swe/paper-metadata-retrieval`
* **Domain**: `constrained paper search`
* **Primary focus**: `Joint semantic and metadata filtering`
* **Primary metric**: `Accuracy@1`
* **Tags**: `constrained paper search`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `16` CPUs, `32 GiB` RAM, `100 GiB` storage; `0` GPU(s)

Build: 1,800 seconds. Eight sequential evaluation invocations: 30 seconds each including startup, APIs and output. No training or fine-tuning. Only documented OpenRouter/Jina resources; no external search or answer collections.

## Public input and output contract

### Inputs

`/task/data/corpus.sqlite` holds 70,000 papers and metadata. Public query/answer JSONL is under `/task/data/validation/`. Requests contain `query_id` and `query`. Distinguish first submission from publication dates and institution location from author citizenship.

### Outputs

Submit executable `/app/build.sh --corpus /task/data/corpus.sqlite --index-dir DIR` and `/app/run.sh --index-dir DIR --queries PATH --output PATH --top-k 1`, plus dependencies under `/app`. Build may start a persistent service. Honor writable index/output/TMPDIR paths under the non-root read-only-code verifier.

Return exactly one `doc_id`/finite numeric `score` item in `results`, preserving `query_id`. A merely related topic or hypothetically adaptable method is insufficient.

## Evaluation

Reward is mean Accuracy@1 across all eight requests. Timeouts zero only their query; failed build, other command failure, invalid output or resource/integrity failure zeros the entire submission.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/paper-metadata-retrieval/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/paper-metadata-retrieval/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/paper-metadata-retrieval/task.toml)
for the complete contract at the synchronized benchmark revision.
