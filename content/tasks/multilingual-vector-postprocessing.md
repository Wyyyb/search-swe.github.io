# Multilingual Vector Postprocessing

Improve cross-language retrieval using only a frozen transform of existing vectors, with **16 GiB RAM**, one GPU and **0.5-second median queries**. Apply the same language-aware function to documents and queries while preserving 1,024 dimensions. Reward is macro nDCG@20 improvement above the frozen baseline; perfect quality is required for full credit, and all learning must finish before verification.

* **Task name**: `search-swe/multilingual-vector-postprocessing`
* **Domain**: `multilingual vector transforms`
* **Primary focus**: `Shared language-aware vector transformation`
* **Primary metric**: `Baseline-normalized macro nDCG@20`
* **Tags**: `multilingual vector transforms`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `16` CPUs, `16 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Offline, one GPU. Five independent rounds each allow 1,800 seconds for preparation with fresh workers, caches and temporary storage; each complete query operation has a 0.5-second median limit across those rounds. Score the ranking from the median-time sample; failed attempts stay in the sample set. All learning/statistics must finish during development. Maintain 1,024 dimensions and apply the same function to documents and queries, independent of batch/order/history.

## Public input and output contract

### Inputs

Frozen multilingual-E5 vectors only: two million training and 200,000 probe vectors in ten languages. Full candidate pools contain 4,880 Belebele and 1,440 XQuAD documents; development has 1,830/1,308 queries. No raw text or encoder checkpoint is supplied.

### Outputs

Submit `/app/submission/transform.py`, frozen weights and dependencies. Implement `load(submission_dir)` and `transform(vectors, languages, state)`. Inputs are read-only FP32 B-by-1024 arrays, B=1–128. Return same-shaped finite real values with nonzero norms. No IDs or phase flag are given. The verifier normalizes results and performs complete-pool cosine ranking; no interaction reranker or verification-time learning is allowed.

## Evaluation

Evaluate 7,170 Belebele and 5,832 XQuAD held-out queries. Binary nDCG@20 averages queries within language, languages within dataset and both datasets equally. With `B=0.9127469497437668`, reward is `clip((Q-B)/(1-B),0,1)`. Matching the frozen baseline earns zero; full credit requires Q=1. Query errors/timeouts zero that query; preparation, resource, frozen-function or integrity violations zero the task. Extra speed gives no bonus.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/multilingual-vector-postprocessing/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/multilingual-vector-postprocessing/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/multilingual-vector-postprocessing/task.toml)
for the complete contract at the synchronized benchmark revision.
