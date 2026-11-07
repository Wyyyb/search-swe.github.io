# Biomedical Graph Retrieval

Translate biomedical questions into graph retrieval on **16 CPUs**, returning the complete answer set within **30 seconds per question**. Multi-hop reasoning must recover every matching node without adding extras; partial sets earn nothing. Reward is exact-set accuracy over 20 questions. Model training and external search are prohibited.

* **Task name**: `search-swe/biomedical-graph-retrieval`
* **Domain**: `biomedical knowledge graphs`
* **Primary focus**: `Multi-hop graph query execution`
* **Primary metric**: `ExactSetAccuracy`
* **Tags**: `graph retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `120 minutes`
* **Compute**: `16` CPUs, `32 GiB` RAM, `100 GiB` storage; no GPU
* **Build limit**: `1,800 seconds`
* **Query limit**: `30 seconds` per question, evaluated sequentially

Implement executable graph retrieval without training or fine-tuning models.
Optional OpenRouter and Jina calls must follow the exact resource allowlist in
`/task/docs/available_resources.md`; external search is prohibited.

## Public input and output contract

### Inputs

* `/task/data/corpus.sqlite` — the supplied biomedical graph.
* `/task/data/validation/queries.jsonl` — eight public example questions.
* `/task/data/validation/ground_truth.jsonl` — their complete answer sets.

Twenty held-out questions exercise different graph query plans.

### Outputs

Place all submission code and dependencies under `/app` and provide:

~~~bash
/app/build.sh --corpus /task/data/corpus.sqlite --index-dir /app/index
/app/run.sh --index-dir /app/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

The verifier rebuilds once, then invokes the runner separately for each question.
Submission code runs as an unprivileged user with `/app` read-only; put writable
indexes, caches and temporary state in the supplied index directory.

~~~json
{"query_id":"example","answer_ids":[123,456]}
~~~

Return distinct integer node IDs. Answer order does not matter.

## Evaluation

A question earns one only when the returned set exactly equals its complete
reference set. Partial answers and supersets earn zero. Reward is mean
ExactSetAccuracy across all 20 questions; the displayed score is 100 times that mean.

A per-question timeout contributes zero for that question. Build failure,
non-timeout execution failure, invalid output or a failed mandatory trajectory
compliance audit sets the overall reward to zero. The audit does not judge relevance.

The integrity audit runs independently three times. Its reported value is the mean of the three binary decisions; all three must accept for a positive task reward. Missing, failed or malformed audit evidence invalidates the measurement.

The full contract is in the benchmark's [task instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/biomedical-graph-retrieval/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/biomedical-graph-retrieval/README.md),
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/biomedical-graph-retrieval/task.toml).
