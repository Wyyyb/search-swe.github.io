# Leaderboard data and publication

The current homepage contains **47 tasks (24 CPU, 23 GPU), two models,
and 94 selected trials** from the 2026-11-09 final archive. GPT-6.1 Terra scores
42.5322347241 and GPT-6 Luna scores 13.1030991867 on the 0–100 mean-task scale.
`selection.json` explicitly allows these two models; other archived models are
not imported. Old result snapshots and generated routes have been removed.

The public package is `.build/hf-trajectories-luna-terra/`: 32,469 inventoried payload files plus the inventory itself,
approximately 1.04 GiB. It includes all 94 ATIF trajectories and all 94 original
coding session text exports, with credentials redacted and host paths normalized.
Large binary artifacts remain listed by name and size without content downloads.
Original benchmark records are never modified.

The prepared replacement plan is `.build/hf-replacement-luna-terra.json`.
It removes the old `releases/2026-10-30-3090361873/` directory from HF main
(44,952 files, approximately 1.61 GiB), and replaces it with the new release.
**Remote replacement is complete.** `storage.json` pins verified HF commit
`1f675a76e0eb10ca5dfb514287c836904c923f18`. All 32,470 public files passed remote
hash/size checks; anonymous JSON/gzip downloads and CORS checks passed. The old
release directory is absent from the current HF tree. Production pages use only
this immutable revision.

To reverify or finish an interrupted activation, run from this repository using the existing HF login:

```bash
python scripts/replace_hf_trajectories.py --apply
```

This one command uploads and verifies the new release, commits old-release
removal and new metadata together, verifies anonymous downloads and CORS, then
pins `storage.json` to the actual immutable HF commit and builds production pages.
Repeat the same command after interruption. It does not commit or push GitHub.
Hub metadata requests explicitly use the existing login. HTTP 429 responses wait
for the server's reset time (or bounded exponential backoff); pagination retries
the affected page. Public browser downloads remain anonymous. No package or plan
rebuild is needed after a rate-limit error during the initial repository query.
Historical HF commits remain accessible; the cleanup affects the current tree.
See [the publication guide](../../docs/leaderboard-publication.md) for details.

To reproduce the local preparation from the current archive:

```bash
python scripts/import_final_results.py
python scripts/replace_hf_trajectories.py --prepare
python -m http.server 7788 --bind 127.0.0.1
```

Open <http://localhost:7788/leaderboard/>. Reuse an existing server on that port.
The importer reads `INDEX.csv`, each `FINAL_RESULT.json`, native result/reward,
and original session receipts directly; no stale analysis directory is needed.
The source file inventories authenticate all exported text and selected inputs.
The package, original response usage, previous-site backup, plan and receipts are
under `.build/` and excluded from Git. `release.json`, `costs.json`, and generated
HTML contain the new compact website results. Production builds reject local
preview URLs. Rebuilding a local preview requires reactivating the verified HF
release before a production deployment.

## Typography and result tables

Leaderboard pages use locally hosted Geist for UI text and Google Sans Code
for code/logs. Font sources and SIL OFL licenses are in `assets/fonts/`; no
external font service is required. Task results show repository task slugs, with 14px table text and approximately
46px desktop rows. Human-readable titles remain searchable.
Narrow screens scroll the table horizontally instead of shrinking its text.

## Data and statistics

- Final selections come only from `final-trajectories/INDEX.csv` and each
  `FINAL_RESULT.json`. Native result/reward files and source file inventories
  authenticate the selected evidence. Analysis summaries from older releases
  are not used.
- Native reward × 100 equals the selected task score. Selection scores already
  use 0–100 and must not be scaled again. Every task has equal weight; CPU and
  GPU use fixed subsets. The importer requires matching complete coverage.
- A valid zero remains a valid measurement. Agent completion is separate and
  appears in Agent. Original execution duration includes tools and waiting,
  excluding setup and verification. When Harbor lacks original execution times,
  paired session start/complete events are used. Three trials have no recorded
  coding end time and display a missing duration; regrade time is never substituted.
- Total tokens in the main leaderboard sum input (including cache) + output
  across the selected All / CPU / GPU task set, not a per-task average. Entry rows
  show Input Tokens, Output Tokens and Cached Tokens; trial summaries show the
  cached subset below Input Tokens.
  Additional reasoning counters appear in Agent. Reasoning is not added a second
  time. Verifier/task-internal API usage is excluded. Regrading uses original
  coding usage once. Missing values remain missing.
- Cost sums selected coding responses at the frozen official USD API rates in
  `official-pricing.json`, checked 2026-11-09. Both models use standard processing,
  30-minute cache writes, and per-request long-context rates above 272,000 input
  tokens. Cache reads/writes are subsets of input and charged once; reasoning
  is already included in output. Sources and pricing assumptions remain public.
- `scripts/leaderboard_costs.py` matches native response usage to every selected
  task/model/effort, verifies trajectory hashes and all published token totals,
  deduplicates response IDs, and calculates with decimal arithmetic before
  display rounding. `costs.json` binds the derived amounts to the exact result,
  usage and pricing snapshots. Rebuild it when any of these inputs change;
  stale or partial cost coverage fails the page build.
- Cost metadata is maintained by the website separately from the verified HF
  trajectory release. `/leaderboard/results.json` downloads the result summary
  with costs, pricing sources and immutable HF trace URLs. The original
  `release.json`, its verified hash, and the HF files remain unchanged.
- Release Date is recorded with its source in `model-metadata.json`, not the evaluation date. The importer reads
  and fingerprints the model metadata, exporting each date and its source URL.
  Missing dates display as a dash and sort last in either direction.
- Regrading is a replacement score, not an additional independent trial.
  Original trajectory and final reward hashes remain separately visible.

The main table shows `Model (effort)` and `Agent (vVersion)` on one line. Provider
information remains in entry details. Score, Release Date, Total tokens and Cost can
be sorted in either direction using the column headers or Sort selector. Sort
state survives scope changes, search, reloads and navigation back from an entry;
ranks continue to reflect scores in the selected task scope. Old `sort=score`
and `sort=tokens` URLs retain their previous descending-score/ascending-token
meaning. Entry task tables also support both score/token/cost sort directions, and
keep Hardware and Agent centered, with the version inline as `Codex (v0.164.0)`. The main board omits metric cards and agent time. Entry rows include Provider
and Agent time, with the individual trial's Cost before the final Trajectory column; durations use
`2h 5min` / `35min`. Scores are labeled with `(%)`.
Trial summaries show six metrics: score, input tokens (with cached tokens as a
secondary line), output tokens, duration, Cost and step count.
Entry and trial pages share the main board's short pricing note. Amounts display
in USD with two decimal places; totals and sorting use unrounded values.

The leaderboard defaults to **Table**; **Pareto** shows total cost versus mean
task score for the same All / CPU / GPU selection. Its cost axis is logarithmic
(linear if a genuinely free model is present). Hover or keyboard-focus points
for values, and follow points or legend links to model results. View, search,
scope and sort survive reloads and the return link from an entry. Search hides
models without redefining which models are Pareto-optimal in the selected
hardware scope. Dominance uses unrounded values; equal points do not dominate
one another. The chart is rendered locally from the embedded summary, with no
chart library, inference calls or additional trajectory downloads.

## Viewer and export boundaries

The leaderboard fetches no trajectories. A trial shows a continuous timeline,
loading steps in batches as the reader scrolls down and keeping loaded steps
above. Long messages initially show six lines, with Show more / Show less
controls; short messages remain fully visible. Tools show compact summaries and expand to reveal input/output. Setup
context and recorded reasoning are collapsed initially. Step links still jump
directly to the relevant position; earlier steps can be prepended. The timeline
uses the full reading width without a step sidebar. Long text and exceptionally
large groups of parallel tool calls are split further. Downloads contain the
text export in compressed ATIF JSON, not the complete jobs directory.

Each step has a compact metadata row: step number, time since the preceding
recorded step, time since the first recorded step, agent, model, and recorded
input/cache/output tokens. Timing is calculated against the complete original
step index, so direct links and filters do not reset it. Time differences include
tools and waiting; they are not isolated model latency. Hover over times for
their meaning and the original timestamp, and over token counts for exact values.
Missing counts stay missing (`—`); cached tokens are included in input and
reasoning is not added to output again. Per-step ATIF usage is preserved as
recorded and is not used to replace the separately deduplicated run totals.
Unverified ATIF dollar estimates are not shown in the step metadata.

## Trial evidence tabs

| Tab | Content |
| --- | --- |
| Trajectory | Continuous structured coding conversation and tool calls. |
| Agent | Directory tree of native agent logs, session recordings and trajectory JSON; coding time/usage below the browser. |
| Verifier | Final score, native reward, evaluation reports and verifier logs. |
| Artifacts | Collected submission files, code previews, trajectory/report downloads and provenance. |
| Config | Saved Harbor configuration and the compact evaluation settings summary. |
| Lock | Resolved Harbor configuration and task fingerprints. |
| Log | Harbor trial lifecycle log. |
| Exception | Saved exception text and/or structured exception information; an explicit empty state when none was recorded. |

Agent, Verifier and Artifacts use a directory tree with collapsible folders,
compact single-child paths, and search that preserves matching ancestors.
Selecting a file opens it in a fixed-height preview with wrap, copy and download
controls. JSON is colored without interpreting file content as HTML.

Files are exported by `scripts/export_trial_files.py` during import and indexed
in each trial's `files/index.json`. Their text is fetched only after opening the
relevant tab and selecting a file. Large text is loaded in parts, and available
text exports can be downloaded as gzip. File bodies are inserted as text.

Agent/artifact/config/lock/log/exception sources are the Harbor directory
accompanying the selected trajectory. Verifier sources **always** follow the
`FINAL_RESULT.json` final reward pointer. The Verifier tab opens the root `reward.json` by default; nested repeated-judge
rewards remain browsable as supporting evidence. When a trial was regraded separately,
the final grading files are in a separate reevaluation directory. Old neighboring verifier rewards
must not replace these final results. Config/Lock can describe the retained
Harbor run rather than a subsequent separate scoring pass; the Verifier note
identifies separately regraded trials. Exceptions do not imply invalid scores.

The file catalog includes binaries and large artifacts with their original
sizes, without copying indexes, databases, model weights or archives. Previews
cover source code and small artifact text, final reports and verifier logs,
plus the saved agent logs/configuration/lock/lifecycle/exception files. Text
limits are 2 MiB per file and 8 MiB per section, except Agent (32 MiB per file
and 64 MiB per section); small
artifact data files use a 256 KiB limit. Files outside this text export remain
listed with a reason and have no download link. Hidden files and symlinks are excluded. Native session JSONL files are included
under their original directory paths. Environment values and credential
fields in JSON and JSONL are redacted; variable references remain visible. The original
files are unchanged. Exported source hashes refer to original bytes, before
redaction or JSON formatting.

Old `?tab=evaluation` and `?tab=configuration` links map to Verifier and Config;
`?tab=agent-logs` also opens Agent.

Tools and observations are joined by nonempty recorded call IDs, including
multiple outputs and missing/unmatched observations. Empty IDs are never joined
across steps: an unambiguous anonymous call uses only its step-local observations;
ambiguous outputs remain visible as unmatched observations. The viewer preserves
the recorded order. Nested agent commands remain as recorded; it does not
invent child sessions or reconstruct missing hierarchy. Embedded image/binary
payloads are preserved as text, without an image renderer in this prototype.

Search loads a per-trial word index only when requested. It matches all query
words across messages, recorded reasoning, tool inputs and outputs, including
unopened chunks. It is word matching, not phrase/substring search. Long encoded
binary strings are excluded from the search index, but preserved in the reader
and download. No output is silently truncated; long text has a load-more button.

Trajectory content is inserted as text, never HTML. The exporter selects fields,
omits environment dictionaries and native configuration extras, and redacts
recognizable credential patterns consistently in chunks, search and downloads.
This automated pass is not a full public-release review. Source logs are
unchanged; exported JSON contains no local host source paths in its metadata.

## Verification

```bash
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/import_final_results.py --check
python scripts/build_leaderboard.py --check
python scripts/leaderboard_costs.py --usage .build/hf-trajectories-luna-terra.usage.json --check
python scripts/build_tasks.py --check
node --check leaderboard.js
node --check leaderboard-pareto.js
node scripts/test_pareto.cjs
node --check trajectory-viewer.js
node --check trial-files.js
```

With Playwright available in the Node module search path and the preview server
running, run `node scripts/test_leaderboard_browser.cjs`. Set
`LEADERBOARD_ORIGIN` to use a different local server address.
Run `node scripts/test_leaderboard_costs_browser.cjs` for cost sorting, chart/table
parity across hardware scopes, keyboard tabs, links, empty states and mobile layout.

The importer check verifies the complete prepared package and its match to the
local website snapshot; it does not modify files. Static summaries also work without
JavaScript. Browser acceptance includes desktop/mobile layouts, scope and
search persistence, direct step links, lazy long outputs, full-text search,
download links, and a retry after a failed chunk request.
