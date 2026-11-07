# Long-PDF Sentence Evidence — Vectorless

Find up to **five supporting sentences** in a 2,043-page novel, using **no embeddings**, a CPU-only index and **900 seconds per query**. The source PDF and sentence inventory become inaccessible after build. Recover evidence that jointly supports an interpretation, not just a related scene. Quality averages three independent semantic-support judgments per question; the full query phase also has a shared 1,800-second limit.

* **Task name**: `search-swe/long-pdf-evidence-vectorless`
* **Domain**: `in-document evidence retrieval`
* **Primary focus**: `Index-only sentence evidence without embeddings`
* **Primary metric**: `SentenceEvidenceAccuracy`
* **Tags**: `vectorless evidence retrieval`, `search-swe`

## Runtime and requirements

* **Agent budget**: `120 minutes`
* **Compute**: `16` CPUs, `16 GiB` RAM, `100 GiB` storage; no GPU
* **Build limit**: `2,400 seconds`
* **Query limits**: `900 seconds` each; `1,800 seconds` shared by the query phase
* **Concurrency**: up to five queries; an additional `60 seconds` allows cleanup
* **Verifier budget**: `14,400 seconds`

Embeddings are prohibited at every stage, including local models, endpoints and
precomputed vectors. Lexical indexing, document structure and documented generation
or non-embedding reranking are allowed. Only build may read the source corpus.
All corpus-derived query state must be persisted inside the index directory.

## Public input and output contract

### Inputs

* `/task/data/corpus` — the 2,043-page War and Peace PDF and `sentences.jsonl`, a fixed inventory of 28,798 units with `sentence_id`, `text` and `pages`.
* `/task/data/validation/queries.jsonl` — ten public questions with `query_id` and `query`.
* `/task/data/validation/golden_answers.jsonl` — support requirements and sufficient reference sentence evidence.

Twelve evaluation questions use different reference units. Physical page numbers
provide provenance; they are not the scored output. Public references are examples
of sufficient evidence, not the only acceptable sentence combinations.

### Outputs

Submit executable scripts and dependencies under `/app`:

~~~bash
/app/build.sh --corpus /task/data/corpus --index-dir /app/index
/app/run.sh --index-dir /app/index --queries /path/to/queries.jsonl --output /path/to/results.jsonl --top-k 5
~~~

The verifier rebuilds, stops all build workers and revokes access to the PDF and
sentence inventory before revealing queries. Search must run from the persisted
index alone. Optional query-time services must start from that index after restart.
Commands run unprivileged; public validation files are not mounted.

~~~json
{"query_id":"example","results":[{"sentence_id":"inventory-id","sentence":"complete inventory text"}]}
~~~

Use exactly these fields and return zero to five distinct complete inventory
units, totaling at most 16,000 sentence characters. Text must match the identified
unit after NFKC and whitespace normalization. Do not add pages, scores, generated
answers, paraphrases or partial sentences. Empty results are valid and score zero.

## Evaluation

Reward is mean SentenceEvidenceAccuracy over twelve questions. After checking source hashes and sentence membership, judge each fixed evidence set independently three times and average the binary support decisions; retrieval runs once. Evidence must fully support the requested interpretation, including comparisons, qualifications and causal links. Alternative original sentences are accepted, but topical overlap, contradictions or unresolved referents do not establish complete support.

Invalid, missing, failed or timed-out queries remain in the denominator with
zero, without erasing other successful queries. Shared build/setup failure
prevents scoring. Judge API or parsing failures invalidate the measurement and
fail closed with zero reward; they are reported separately from retrieval errors.

Configure the verifier-only `ANSWER_JUDGE_MODEL_NAME`, `ANSWER_JUDGE_BASE_URL` and `ANSWER_JUDGE_API_KEY`; the endpoint must satisfy the task’s verifier network policy. The evidence judge uses high reasoning effort and temperature zero, within a 5,400-second budget. Its credentials and model permission are not granted to submission code. A separate 3,600-second
trajectory audit must return a valid binary pass to preserve the 0–1 accuracy reward.

The full contract is in the benchmark's [task instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/long-pdf-evidence-vectorless/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/long-pdf-evidence-vectorless/README.md),
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/long-pdf-evidence-vectorless/task.toml).
