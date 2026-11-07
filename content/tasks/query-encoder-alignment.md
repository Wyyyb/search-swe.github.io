# Query-side Encoder Alignment

Align a **0.6B query encoder** to fixed document vectors on one GPU, using at most **60% of the measured 4B reference runtime**. Improve top-one accuracy above a separately measured 0.6B ridge baseline without changing the document space. Reward normalizes that accuracy gain; runtime is a gate, measured over five fresh processes, whose candidate outputs must match exactly.

* **Task name**: `search-swe/query-encoder-alignment`
* **Domain**: `query encoder optimization`
* **Primary focus**: `Query adaptation to a frozen document space`
* **Primary metric**: `Accuracy@1 error reduction above frozen 0.6B ridge, after runtime gate`
* **Tags**: `query encoder optimization`, `search-swe`

## Runtime and requirements

* **Agent budget**: `6 hours`
* **Compute**: `8` CPUs, `32 GiB` RAM, `100 GiB` storage; `1` GPU(s)

Use Qwen3-Embedding-0.6B as the basis. Development has allowlisted egress, but external retrieval, reranking, embedding, generation and answer services are prohibited. Final inference is offline. Each reference/candidate invocation has 1,800 seconds; task-specific verification has 20,400 seconds within a 22,200-second overall verifier including audit.

Final query inference must use the supplied `Qwen3-Embedding-0.6B` encoder or a legitimately adapted derivative, and its outputs must contribute to candidate selection or ranking. Development-only use, loading unused weights or discarding encoder outputs does not satisfy this requirement. Lexical, structural and corpus-copy features may supplement the required encoder, but cannot replace it.

## Public input and output contract

### Inputs

8,674 fixed document vectors in `/task/data/doc.npy` and corresponding corpus rows; 100 public query/label pairs under `/task/data/validation/`. `/app/quality_reference` supplies fixed 0.6B centered-ridge quality baseline. The 4B starter/model may provide public-input teacher signals and timing comparisons, but is inaccessible to final inference.

### Outputs

Submit all custom runtime files under `/app/submission`, including:

~~~bash
/app/submission/run.sh --doc-vectors /task/data/doc.npy --queries /path/to/queries.jsonl --output /path/to/results.jsonl --top-k 1
~~~

Preserve vector bytes and row order. Return one valid `doc_id`/finite `score` result per `query_id`, in input order. Exclude same-ID documents and full-text matches after NFKC, whitespace collapse and casefold. Ties follow corpus order. All five fresh-process candidate runs must produce byte-identical output. Use supplied scratch and leave no background processes.

## Evaluation

A0 is the measured hidden Accuracy@1 of the fixed 0.6B centered-ridge baseline, fit only on public corpus text/vector pairs. Reward is `clip((Accuracy@1-A0)/(1-A0),0,1)` provided candidate runtime is at most 60% of the separate measured 4B time reference.

Timing includes startup, imports, loading, encoding, retrieval/filtering, output and exit, without warmup or cache flushing. The quality reference is fit and run once, followed by five time-reference/candidate pairs. Each system’s median complete wall time determines the runtime gate; all candidate outputs must be byte-identical and the time reference must remain deterministic. The 4B accuracy is diagnostic. Reference failure or A0=1 invalidates measurement; format, vector-integrity, timeout or audit failure yields zero.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/query-encoder-alignment/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/query-encoder-alignment/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/query-encoder-alignment/task.toml)
for the complete contract at the synchronized benchmark revision.
