# ICSI Meeting Memory

Compress 67 meetings into **183,981 bytes of readable memory (5% of dialogue text)** and answer from at most **ten retrieved notes**, without a local model or GPU. The transcripts disappear after preparation, and the answerer gets at most two generation calls. Credit requires both preserved evidence and a correct answer; the reference quality maps to 20/100. Topic matching alone is insufficient.

* **Task name**: `search-swe/icsi-meeting-memory`
* **Domain**: `compact meeting memory`
* **Primary focus**: `Evidence preservation under memory compression`
* **Primary metric**: `Joint evidence-and-answer accuracy`
* **Tags**: `compact meeting memory`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `8` CPUs, `8 GiB` RAM, `8 GiB` storage; `0` GPU(s)

No local model or GPU. Build: 300 seconds; all searches together: 150 seconds; all answers together: 1,800 seconds. Jina is allowed for preparation/search, while permitted generation is restricted to answering. Evaluation uses restricted API transports, not provider credentials in submitted processes.

### Host configuration

The answerer gateway requires `OPENROUTER_API_KEY` with the [shared 47-model profile](https://github.com/VectorSpaceLab/Search-SWE/blob/main/docs/evaluation/submission-models.md), further restricted to four generation models by this task. `JINA_API_KEY` is optional. Evidence/answer grading uses separate `ANSWER_JUDGE_MODEL_NAME`, `ANSWER_JUDGE_BASE_URL` and `ANSWER_JUDGE_API_KEY`; trajectory auditing uses `VERIFIER_OPENAI_API_KEY` and `VERIFIER_OPENAI_BASE_URL`. Endpoints must satisfy the verifier network policy.

## Public input and output contract

### Inputs

`/task/data/history.jsonl` covers 67 meetings. Five public questions, reference answers and evidence are under `/task/data/validation/`; 143 evaluation questions are withheld.

### Outputs

Deliver exactly four regular files: `/app/memory.json`, `build.sh`, `run.sh`, `answer.sh`. Memory must be readable JSON of at most 183,981 bytes; do not compress or encode dialogue. Scripts must be self-contained and corpus-independent.

~~~bash
/app/build.sh --memory /app/memory.json --output /path/to/index
/app/run.sh --index /path/to/index --question "$question" --output /path/to/memories.json
/app/answer.sh --question "$question" --memories /path/to/memories.json --output /path/to/answer.txt
~~~

Search returns at most ten strings from the indexed memory. Answer returns nonempty plain text of at most 2,000 characters, using at most two generation calls with at most 2,000 output tokens each. Build, search and answer have separate read boundaries: original transcripts do not transfer, search sees only the index, and answer sees only the current question and recalled notes.

## Evaluation

For each question, credit requires both an evidence hit and a correct answer.
A hit means that the retrieved notes faithfully preserve at least one relevant
reference fact, including valid summaries or paraphrases. Topic overlap alone
does not count. The answer judge checks the reference answer and required facts.
Evidence is judged without the answer, and the answer is judged without the
retrieved notes.

Evidence extraction and answer generation run once. The fixed evidence and answer are each judged three times; a round earns one only when both judgments pass. Average the three joint decisions per question, then all 143 held-out questions equally. Transport retries do not add samples or regenerate the answer.
Evidence and answer accuracy are also reported separately. Semantic grading
remains subject to model variability.

### Reward mapping

For raw quality `Q`, use `b=0.06293706293706294` and `a=0.2`:

```text
reward = a * Q / b                         if Q <= b
         a + (1-a) * (Q-b) / (1-b)         if Q > b
```

This maps quality 0, b and 1 to scores 0, 20 and 100. The reference is a positive-score milestone, not a minimum quality gate. Validity and audit requirements still apply; diagnostics do not change the reward.

### Validity and failure handling

The four files, executable permissions, JSON syntax and size, index build,
script completion and output formats must satisfy the contract. A failed
submitted process or invalid output invalidates the submission. Empty retrieval
is an evidence miss. A malformed judge response or model-service failure
invalidates the measurement rather than establishing model quality.

A separate integrity audit must accept the trajectory and submission. Audit-service failures invalidate the measurement; a valid rejection gives zero reward.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/icsi-meeting-memory/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/icsi-meeting-memory/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/icsi-meeting-memory/task.toml)
for the complete contract at the synchronized benchmark revision.
