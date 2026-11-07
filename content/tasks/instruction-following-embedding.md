# Instruction-following Embedding

Make query embeddings obey changed relevance instructions with a **512 KiB deployment payload**, one E5 forward pass and **one-second median queries**. Document vectors remain fixed. Reward measures how much rankings respond to the instruction change, normalized against FollowIR-7B, while six relevance checks must retain at least 90% of their query-only references. Serving uses one GPU.

* **Task name**: `search-swe/instruction-following-embedding`
* **Domain**: `compact query adapters`
* **Primary focus**: `Instruction-sensitive ranking with compact adaptation`
* **Primary metric**: `Harmonic mean of three positive subset p-MRR values (otherwise zero), gated by six nDCG@10 checks`
* **Tags**: `compact query adapters`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `16` CPUs, `32 GiB` RAM, `32 GiB` storage; `1` GPU(s)

Offline, one GPU. Deployment increment: 512 KiB (524,288 bytes) for all JSON/safetensors. Final serving uses one complete E5 forward per query, fixed tokenizer/input format and mean pooling. Preparation: 3,600 seconds; each query/instruction version: a one-second median across five complete measurements, including 1,000-candidate scoring. The median measurement supplies its ranking; timeouts stay in the sample set, and malformed output invalidates the pair.

## Public input and output contract

### Inputs

E5-large-v2, 1,717 training records, 98,312 corpus passages and 20 public paired-instruction groups are supplied; 84 groups are held out. Public group labels are validation-only: no gradient training, teacher targets or label-aware mining. Corpus text may independently serve as unlabeled anchors.

### Outputs

Submit `/app/submission/submission.json` with exactly `query_checkpoint` and `document_checkpoint`; document must be `base`. Query may be `base` or a safe relative standard PEFT LoRA directory containing configuration and safetensors. No custom code, tokenizer, output transform or document cache is deployed. Training may use larger intermediate models, but final weights must fit the payload and fixed serving rules.

Query text uses two lines, separated by a real newline:

~~~text
query: {query}
Instruction: {instruction}
~~~

Document text uses `passage: {text}`. Serving fixes right truncation to 512 tokens, FP32 mean pooling over nonpadding tokens and L2 normalization. Document encoding stays unchanged; query workers cannot inspect candidates or rankings.

## Evaluation

For documents relevant under the original instruction but excluded by the revised one, p-MRR uses `(y-x)/max(x,y)`, where x/y are original/revised ranks and missing candidates have rank 1,001. Lowering an excluded document increases this value. Average documents within each group, then groups within each subset to obtain P. H is the harmonic mean of the three positive subset values, or zero if any is nonpositive.

Six subset/version nDCG@10 gates require at least 90% of frozen query-only reference quality. After those gates, reward is `clip(H/0.10647366293851011,0,1)` with B=0. The upper anchor is FollowIR-7B’s measured harmonic p-MRR on this task’s 84 hidden groups, using the official prompt and 2,048-token truncation; it is an external quality reference, not a deployable model or theoretical ceiling. Arithmetic macro p-MRR is diagnostic. Failure of either instruction version zeros the group; invalid payload, preparation/resource or audit failure zeros the task. The full source documents the six exact relevance floors.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/instruction-following-embedding/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/instruction-following-embedding/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/instruction-following-embedding/task.toml)
for the complete contract at the synchronized benchmark revision.
