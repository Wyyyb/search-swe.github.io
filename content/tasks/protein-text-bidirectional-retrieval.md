# Protein–Text Bidirectional Retrieval

Learn protein–text retrieval with **64-dimensional vectors** and a **256 KiB total submission**, using one GPU and **P95 query latency at most one second**. Compress learned state while preserving exact paired identity in both directions. A pair earns credit only when protein-to-text and text-to-protein retrieval both rank its counterpart first; semantic similarity alone is insufficient.

* **Task name**: `search-swe/protein-text-bidirectional-retrieval`
* **Domain**: `protein-text embeddings`
* **Primary focus**: `Compact alignment with mutual top-one matching`
* **Primary metric**: `Mutual top-one accuracy, equally weighted across two datasets`
* **Tags**: `protein-text embeddings`, `search-swe`

## Runtime and requirements

* **Agent budget**: `1 hour`
* **Compute**: `16` CPUs, `16 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Offline, one GPU. Entire submission: at most 256 KiB, including code and learned state. Four independent dataset/direction groups each have 900 seconds for preparation, 3 seconds hard query timeout and p95 <=1 second. Final vectors have exactly 64 dimensions.

## Public input and output contract

### Inputs

Supplied ESM-2 150M and BiomedBERT bases under `/task/models/`. Swiss-Prot and ProteinKG25 provide 430,595/422,315 training pairs. Public valid pools keep 10,000 candidates each with only ten labeled pairs per dataset. Evaluation retains strict official pairing, not semantic-equivalence labels.

### Outputs

Submit `/app/submission/encoder.py`, compact frozen weights and dependencies. Define `Encoder(model_root=..., checkpoint_root=..., work_dir=...)` and `encode(values, modality)` for `protein` or `text`, returning finite N-by-64 vectors. Unchanged base models stay outside the payload.

Candidate encoding and single-query encoding run in fresh isolated processes. Candidate caches/state cannot transfer to query encoders; only the trusted scorer retains vectors. It normalizes and ranks by cosine, ties by opaque ID. No query batching, cross-request cache or candidate-interaction reranking is allowed.

## Evaluation

Each of 10,000 official pairs per dataset succeeds only when both independent directions rank its counterpart first. Reward is the equal mean of these two mutual-top1 success rates. Directional Acc@1/Recall@20 are diagnostic. Failed or late queries fail their pair and remain in denominators. Any group’s p95 above one second, preparation failure, oversized submission or resource violation zeros the whole task.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/protein-text-bidirectional-retrieval/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/protein-text-bidirectional-retrieval/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/protein-text-bidirectional-retrieval/task.toml)
for the complete contract at the synchronized benchmark revision.
