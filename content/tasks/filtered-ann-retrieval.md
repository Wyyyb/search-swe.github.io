# Filtered ANN Retrieval

Return exact filtered Top-10 neighbors from **ten million vectors** within **15 ms median latency**, using **8 CPUs and 16 GiB RAM**. A real Faiss ANN index must honor all tag filters and survive relocation. Each query earns credit only when all ten measured responses are exact and identical and both locations meet the latency limit; partial recall earns nothing.

* **Task name**: `search-swe/filtered-ann-retrieval`
* **Domain**: `filtered vector search`
* **Primary focus**: `Exact filtered results with approximate indexing`
* **Primary metric**: `Exact Top-10 success rate after latency and relocation checks`
* **Tags**: `filtered vector search`, `search-swe`

## Runtime and requirements

* **Agent budget**: `2 hours`
* **Compute**: `8` CPUs, `16 GiB` RAM, `64 GiB` storage; `0` GPU(s)

Offline. Build: 600 seconds. Each query: a 15-millisecond median including transmission and JSON response decoding; individual measurements have a one-second execution cap. Build a valid L2 Faiss ANN index and actually use it; full-corpus brute force must not be the default. Index state must survive process termination and relocation.

## Public input and output contract

### Inputs

YFCC-10M: ten million 192-dimensional uint8 vectors in `/task/data/corpus/vectors.u8bin`, tags in `metadata.spmat`. Ten public queries and reference results are under `/task/data/validation/`; an additional small example is supplied.

### Outputs

~~~bash
/app/build.sh --vectors /task/data/corpus/vectors.u8bin --metadata /task/data/corpus/metadata.spmat --index-dir /path/to/index
/app/run.sh --index-dir /path/to/index --serve
~~~

Persist all state as regular files, including `index.faiss`. After loading, emit `{"status":"ready"}`. Requests contain string `query_id`, `vector`, `filter: {"all":[...]}` and k from 0 to 100. Return `query_id` and `results` containing integer `doc_id` values only. Return exactly min(k, matching count), ordered by original squared L2 then ID. All tags must match; boundary ties are accepted. Corpus paths and surviving build processes are unavailable at search time.

## Evaluation

The verifier measures each of 30 hidden queries five times before relocation and five times after relocation. Each pass starts a fresh service and clears scratch; prepared index files are read-only and query-time writes use `TMPDIR`. Both locations must meet the 15-millisecond median, and all ten responses must be valid, exact and identical for a query to earn one. Service loading is outside query timing. Reward is their mean; partial recall earns no credit. Query failures remain local, while build, index, load or required audit failures zero the submission. The verifier requires the documented Landlock isolation support.

The integrity audit runs independently three times. Its reported value is the mean of the three binary decisions; all three must accept for a positive task reward. Missing, failed or malformed audit evidence invalidates the measurement.

See the [full instructions](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/filtered-ann-retrieval/instruction.md),
[task documentation](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/filtered-ann-retrieval/README.md)
and [runtime configuration](https://github.com/VectorSpaceLab/Search-SWE/blob/ed7544f4aeb1fe8a072edc77ece1f2f4a742bfda/tasks/filtered-ann-retrieval/task.toml)
for the complete contract at the synchronized benchmark revision.
