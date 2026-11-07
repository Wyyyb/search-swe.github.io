# Reasoning-intensive Query Rewriting

Retrieve three relevant biology documents across terminology and reasoning gaps, with **16 CPUs**, no GPU and **900 seconds for ten queries**. Build over 57,359 documents using query rewriting, retrieval and reranking within the permitted API policy. Reward is the fraction of questions with at least one relevant document in the top three; rewriting itself receives no separate score.

* **Task name**: `search-swe/reasoning-query-rewriting`
* **Domain**: `biology`
* **Primary focus**: `query rewriting`
* **Primary metric**: `Accuracy@3`
* **Tags**: `information-retrieval`, `query-rewriting`, `reasoning-intensive-retrieval`

## Runtime and requirements

* **Agent time budget**: up to `120 minutes`
* **Build limit**: `1800 seconds`
* **Query-run limit**: `900 seconds` total for the single invocation processing all 10 hidden queries
* **Python**: `3.12`
* **Compute**: `16` CPU cores, `32 GiB` memory, `100 GiB` storage
* **GPU required**: `no`
* **Network**: `restricted` — allowlisted resources only

### Host configuration

When enabling OpenRouter submission resources, configure
`REASONING_QUERY_REWRITING_OPENROUTER_API_KEY` with the dedicated
[17-model profile](https://github.com/VectorSpaceLab/Search-SWE/blob/main/docs/evaluation/submission-models.md):
three generation, nine embedding and five rerank models. Do not substitute the
shared 47-model profile. Coding-agent and judge keys use separate model access.
The CLI checks the enabled key before saving configuration or starting a run.

## Public input and output contract

### Inputs

* `/task/data/corpus.jsonl` — 57,359 biology documents.
* `/task/data/validation/queries.jsonl` — 10 public development queries.
* `/task/data/validation/ground_truth.jsonl` — relevance labels for the public queries.

### Outputs

* JSONL retrieval results — top-3 ranked corpus documents for each input query.

The submission must provide executable `build.sh` and `run.sh` entry points under `/app`.

## Evaluation

The verifier evaluates 10 hidden queries. A query is a hit when at least one relevant document appears in its top three results. Reward is the fraction of queries hit. Execution or output-validation failure, or a failed trajectory audit, sets the final reward to `0`.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/reasoning-query-rewriting/instruction.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/reasoning-query-rewriting/task.toml)
for the complete contract at the reviewed benchmark revision.
