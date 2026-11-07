# Code Embedding Fine-tuning

Fine-tune the supplied BGE embedder **offline in six hours on one GPU**, preserving its architecture and parameter count. Use 5,000 training examples to improve rank-one code retrieval on unseen queries. The verifier fixes tokenization, pooling and exact search; reward is the absolute Accuracy@1 gain over the original checkpoint, not the submitted model’s total accuracy.

* **Task name**: `search-swe/code-embedding-finetuning`
* **Domain**: `code retrieval`
* **Primary focus**: `embedding fine-tuning`
* **Primary metric**: `held-out Accuracy@1 improvement`
* **Tags**: `code-retrieval`, `embedding`, `fine-tuning`, `representation-learning`, `BGE`

## Runtime and requirements

* **Agent time budget**: up to `6 hours`
* **Python**: `3.12`
* **Compute**: `8` CPU cores, `32 GiB` memory, `100 GiB` storage
* **GPU required**: `yes`
* **Network**: `no`

## Public input and output contract

### Inputs

* `/task/data/corpus.jsonl` — the code document corpus.
* `/task/data/train.jsonl` — 5,000 supervised code-retrieval training examples.
* `/task/data/validation/` — 10 public validation queries and relevance labels.
* `/task/models/bge-base-en-v1.5` — the supplied backbone model.

### Outputs

The submission must contain a self-contained offline checkpoint at `/app/submission/model`. It must preserve the backbone architecture, parameter names, parameter shapes, and parameter count, and must be loadable locally by the standard Transformers interfaces.

## Evaluation

Queries are encoded without a prefix; documents use `(title + " " + text).strip()`. Both are truncated to 512 tokens. The final-layer CLS vector is L2-normalized, and retrieval uses exact inner products.

The verifier compares the original backbone and the submitted checkpoint using the same embedding and exact-search procedure on 200 hidden code-retrieval queries. The base reward is the nonnegative absolute improvement in held-out `Accuracy@1`, measured on the 0–1 accuracy scale:

```text
max(0, submitted Accuracy@1 - original-backbone Accuracy@1)
```

Invalid evaluation or timeouts give zero reward; the integrity audit also gates this gain.

The integrity audit runs independently three times. Its reported value is the mean of the three binary decisions; all three must accept for a positive task reward. Missing, failed or malformed audit evidence invalidates the measurement.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/code-embedding-finetuning/instruction.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/code-embedding-finetuning/task.toml)
for the complete contract at the reviewed benchmark revision.
