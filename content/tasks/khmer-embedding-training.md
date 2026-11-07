# Khmer-to-English Embedding Training

Adapt multilingual E5 for Khmer-to-English retrieval **offline in six hours on one GPU**, with only **three labeled question/answer examples**. Preserve the encoder architecture and tokenizer while bridging the language gap. Quality is the fraction of questions with an answer-bearing passage in the top 100; the reference recall of 0.595 maps to 15/100.

* **Task name**: `search-swe/khmer-embedding-training`
* **Domain**: `cross-language training`
* **Primary focus**: `Low-supervision cross-language adaptation`
* **Primary metric**: `Recall@100`
* **Tags**: `cross-language training`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Offline, one GPU. Fresh index build: 12 hours; each query invocation: 30 minutes. Preserve the supplied multilingual-E5 architecture, configuration, parameter shapes and tokenizer. The optional local generative model is development-only.

## Public input and output contract

### Inputs

`/task/data/corpus.parquet` provides `_id`, `title`, `text`; `/task/data/validation/queries.jsonl` and `answers.jsonl` supply only three question/answer examples. Models are `/task/models/multilingual-e5-large` and development-only `/task/models/Qwen3.5-9B`.

### Outputs

Save a complete offline checkpoint at `/app/submission/model/`, including `model.safetensors`, `config.json` and unchanged tokenizer files. Submit executable `/app/build.sh` and `/app/run.sh` with dependencies under `/app`.

~~~bash
/app/build.sh --corpus /task/data/corpus.parquet --index-dir /path/to/index
/app/run.sh --index-dir /path/to/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl
~~~

Build creates the initially absent index; prebuilt corpus indexes are not accepted. Retrieval sees a read-only index. Both stages run as separate non-root users with supplied scratch. Input rows contain `id`, `question`; output rows preserve input order and contain the same `id`, 100 unique zero-based Parquet row `indices` and finite descending `scores`, breaking ties by row number. Return all rows only if the corpus has fewer than 100.

## Evaluation

Recall@100 uses the source answer-token hit rule: a question succeeds when
at least one of the first 100 retrieved documents contains an accepted answer.
Recall@20 is diagnostic.

### Reward mapping

For raw quality `Q`, use `b=0.595` and `a=0.15`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 15 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

The verifier checks local checkpoint loading, preserved architecture and
tokenizer, a successful fresh build, complete query coverage, 100 valid unique
positions per query, finite sorted scores and time limits. Hidden questions,
answer aliases, the generative model and judge credentials are unavailable
to submitted build and retrieval processes.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/khmer-embedding-training/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/khmer-embedding-training/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/khmer-embedding-training/task.toml)
for the complete contract at the synchronized benchmark revision.
