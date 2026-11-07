# Rust BM25 Search

Implement a Rust BM25 engine over **8.84 million passages** using **4 CPUs, 16 GiB RAM and 64 GiB storage**, without an existing search engine. First match the pinned Pyserini quality floor, then improve the geometric balance of ranking quality, median query time and index size. Reference-equivalent performance earns 0.5 reward; falling below the quality floor earns zero.

* **Task name**: `search-swe/rust-bm25-search`
* **Domain**: `lexical passage retrieval`
* **Primary focus**: `Rust indexing and BM25 search efficiency`
* **Primary metric**: `Quality-gated quality/time/index-size reward`
* **Tags**: `BM25`, `Rust`, `inverted-index`, `MS-MARCO`, `CPU`

## Runtime and requirements

* **Agent time budget**: up to `180 minutes`
* **Rust**: `1.85.1`, with locked generic crates available offline
* **Compute**: `4` CPU cores, `16 GiB` container memory, `64 GiB` working storage
* **GPU required**: `no`
* **Network**: `no`
* **Compilation limit**: `600 seconds`
* **Index-build limit**: `7,200 seconds`
* **Query limit**: `120 seconds` per request, including process startup for cold queries
* **Batch limits**: `3,600 seconds` each for warmup and the measured query batch
* **Verifier budget**: `93,600 seconds` overall

Implement indexing, serialization, BM25 scoring and retrieval in Rust. Tune BM25 and text analysis using generic offline crates; search-engine libraries, prebuilt indexes, neural retrieval and external data are prohibited.

Memory includes child processes and page cache. Verification requires Landlock ABI 1+ and seccomp; search runs unprivileged with access only to the executable, immutable index and required system libraries.

## Public input and output contract

### Inputs

* `/task/data/corpus.jsonl.gz` — 8,841,823 passages with `docid`, `text` and `title`. Index only `text`; IDs are decimal strings from `0` through `8841822`.
* `/task/data/warmup.jsonl.gz` — 54 unscored DL20 queries, disjoint from evaluation.
* `/app/submission` — an unimplemented Rust scaffold with pinned Cargo files.

Evaluation queries and judgments are withheld. MS MARCO dataset terms apply; `/task/docs` describes the environment.

### Outputs

Submit `Cargo.toml`, `Cargo.lock` and Rust source under `/app/submission`, limited to 1,000 regular files and 10 MiB. Only source transfers: no binaries, indexes, vendored dependencies or custom build scripts. The verifier recompiles and builds a fresh index:

~~~bash
cargo build --release --offline --locked --bin bm25-search -j 4
bm25-search index --corpus /task/data/corpus.jsonl.gz --index /work/index --threads 4
bm25-search search --index /work/index --threads 4
~~~

The binary is limited to 100 MiB and the read-only index to 16 GiB of logical file bytes, including metadata. All persistent retrieval state must be in the index.

Search is a persistent JSONL process. For each `{"query_id":"example","text":"example query"}` request, flush one response:

~~~json
{"query_id":"example","results":[{"doc_id":"42","score":1.2}]}
~~~

Return up to ten unique IDs with finite descending scores and deterministic ties. Request/response limits are 4,096/65,536 bytes. Send diagnostics only to stderr, emit no startup message, and exit within five seconds of EOF. Sampled cold and warm responses must match exactly, including scores.

## Evaluation

Evaluate 6,980 held-out queries. MRR@10 averages the reciprocal rank of the first relevant top-ten result, with zero for no hit. Every query requires a valid response.

The reference is Pyserini 1.4.0, BM25 `k1=0.9`, `b=0.4`, default English analysis and text-only indexing without stored text, positions or vectors. Its exact MRR@10 floor is `3236243/17589600`; do not round it.

Build each index once, then run five fresh-process batches per system, each after 54 warmup queries, with one request outstanding. Rankings must agree across repeats. Let `M`, `T`, `D` be candidate MRR@10, median batch seconds and index bytes; `Mref`, `Tref`, `Dref` are the reference values:

~~~text
M >= Mref = 3236243/17589600
U = ((M/Mref) * (Tref/T) * (Dref/D))^(1/3)
reward = U / (1 + U)
~~~

Quality, time and disk have equal weights. Invalid, timed-out, over-budget or below-floor submissions receive zero; reference/environment failures invalidate the measurement. Startup latency, latency percentiles, QPS, build time and process RSS are diagnostics, not extra reward terms. OS file caches are retained.

The full contract is in the benchmark's [task instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/rust-bm25-search/instruction.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/rust-bm25-search/task.toml).
