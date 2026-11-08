# Leaderboard：从本地预览发布到 Hugging Face

官网保持静态 HTML/CSS/JS。榜单及任务分数随网站发布，轨迹、日志和文件预览
从公开的 HF Dataset [`search-swe/trajectories`](https://huggingface.co/datasets/search-swe/trajectories)
匿名按需读取。浏览器不需要 HF Token。

## 当前更新：Luna + Terra 的 94 条最新轨迹

2026-11-09 版本只展示 `openai/gpt-6-luna` 和 `openai/gpt-6.1-terra`，
每个模型 47/47 道题。数据源：
`/data/Search-SWE-Workspace/Search-SWE/run-eval-release/Search-SWE/jobs/final-trajectories`。
旧模型结果、旧 snapshot 和旧 trial 页面已从本地官网替换。

HF 上传、旧轨迹清理和全部校验已完成，官网数据已固定到提交
[`1f675a76e0eb10ca5dfb514287c836904c923f18`](https://huggingface.co/datasets/search-swe/trajectories/commit/1f675a76e0eb10ca5dfb514287c836904c923f18)。
32,470 个公开文件的哈希、大小及匿名下载/CORS 检查均已通过，旧 release 已从当前树删除。
下列命令保留用于同一版本的幂等复核或中断恢复，正常情况下不必再次执行：

```bash
python scripts/replace_hf_trajectories.py --apply
```

仓库查询、分页清单和哈希核验使用已有 HF 登录，公开下载/CORS 检查仍不携带凭证。
遇到 429 时，脚本遵守 `Retry-After` 或 `RateLimit` 的重置时间等待；没有这些头时
按 60、120、240、300 秒退避，最多重试六次，并打印等待进度。
目录扫描只重试当前 HTTP 页，不重新扫描整棵目录。此修复不改变发布包或删除计划，
先前在仓库查询阶段遇到 429 的执行可直接用同一命令重试，无需重新导出。

脚本和计划将目标固定为 `search-swe/trajectories`。本次操作范围：

- 删除旧目录 `releases/2026-10-30-3090361873/`：44,952 文件，1,730,574,592 字节。
- 上传 `.build/hf-trajectories-luna-terra/` 的公开包：32,469 个清单内文件及清单本身，约 1.04 GiB，94 条轨迹。
- 更新 Dataset README 和 `publication.json.gz`。保留 `.gitattributes` 和其他非轨迹文件。
- 验证成功后，自动更新 `content/leaderboard/storage.json` 并生成 98 个 HTML 页面及结果 JSON。

运行过程先上传新 release，校验所有远端文件的大小、Git/LFS 哈希、匿名下载和 CORS，
再以固定父提交把旧目录删除和新元数据提交在一起。上传或校验失败不会先删掉旧数据。
脚本会检查旧文件是否被其他人修改；发现并发改动则停止清理。中断后重跑同一命令即可：
已上传文件可续传，已成功但回执丢失的提交会被识别并继续验证。

删除作用于 HF 当前版本，历史提交保留，不删除整个 dataset、不重写历史。
脚本不会修改原始评测目录，也不会执行 GitHub commit、push 或网站部署。
HF 验证完成后才可提交官网变更；部署前运行：

```bash
python scripts/build_leaderboard.py --production --check
```

不带 `--apply` 只核对本地包和操作范围，不发出 HF 请求或修改远端。
依赖已安装；换机器时用 `python -m pip install -r scripts/requirements-hf.txt`。

## 当前版本的本地重建与审计

```bash
python scripts/import_final_results.py
python scripts/replace_hf_trajectories.py --prepare
python scripts/import_final_results.py --check
python scripts/leaderboard_costs.py --usage .build/hf-trajectories-luna-terra.usage.json --check
python scripts/build_leaderboard.py --check
```

`--prepare` 仅通过只读 HF 请求记录基准版本和删除范围。已有计划会重新校验，
不会默默替换已审核的目标。新归档应使用新的 `--package` 和 `--plan` 路径。
本次计划为 `.build/hf-replacement-luna-terra.json`；完成回执为相邻的
`.applied.json` 和 `hf-trajectories-luna-terra-uploaded.json`。备份保存在
`.build/hf-trajectories-luna-terra.previous-site.json`。

评分沿 `FINAL_RESULT.json` 的最终 reward 指针读取，支持标量 reward，
用量来自原始 coding session 中按 response ID 去重的 `token_usage_record`。
两条原生汇总少计末尾响应的轨迹使用完整请求记录，具体说明保存在 Agent tab。
重评分只替换 verifier，不重复计入解题用量；缺少原始结束时间的三条轨迹显示缺失时长。
官方 qualification 标记和限制说明保留在 Verifier tab 和结果下载中。

Cost 采用 `official-pricing.json` 保存的官方标准处理 USD 价格，包含缓存读写和
逐请求长上下文档位。2026-11-09 核实的来源为
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)、
[Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra) 和
[官方价目表](https://developers.openai.com/api/docs/pricing)。
不是账户账单，也不包含 verifier、任务内 API 或基础设施费用。
仅更新价格时可以单独重算 `leaderboard_costs.py`，无需重新上传轨迹。

公开包包含全部 94 个 ATIF 下载及 94 份原始 session 文本导出；预览与下载使用
相同的脱敏文本。主机路径替换为文档化别名，凭证和环境值脱敏。
二进制索引、大模型文件等只列名称、大小和不可预览原因，不上传其内容。

## 历史记录：2026-11-04 GLM 下架

2026-11-04 从网站移除 `z-ai/glm-5.3-flash`。当时网站为 **47 道题、3 个模型、
141 份结果**；其他模型的结果、费用和 entry/trial 链接不变。原始 jobs 不修改。

当时 HF 删除及校验完成，固定版本为
[`824b6d863b69b1f86b9d73b365dca28af200de7c`](https://huggingface.co/datasets/search-swe/trajectories/commit/824b6d863b69b1f86b9d73b365dca28af200de7c)。
当时 `storage.json` 切换到该版本并移除 pending 标记，146 个 HTML 页面及结果 JSON
使用该固定版本。本节为历史记录，现行版本见本文开头。

以下命令保留用于离线审计或中断后的重试，正常情况下无需再次执行删除：

```bash
python scripts/prune_hf_models.py          # 离线核对并列出删除范围
python scripts/prune_hf_models.py --apply  # 执行 HF 删除、校验并更新本地官网
```

已使用 `.build/hf-trajectories-without-glm/` 和
`.build/hf-model-removal-2026-11-04.json` 完成 `search-swe/trajectories` 的更新，
删除了 GLM 的 **47 个 trial 目录、15,183 个文件，约 539.06 MiB**。
同一提交中更新了 `README.md`、release 的 `snapshot.json` 和 `publication.json.gz`；
其余 141 份轨迹逐字节保留，不重复上传。

脚本复用 `hf auth login` 或 `HF_TOKEN`。提交以
`4ad9ff8ac4c70eefa3d5f6781df3692d81adfc7b` 为父提交；远端发生其他变化时会拒绝
自动删除。中断后重跑 `--apply`：若同一提交已经成功，则验证结果并继续接入网站。
校验包括保留文件哈希、删除目录缺失、匿名下载和 CORS。

执行回执为 `.build/hf-model-removal-2026-11-04.applied.json` 和
`.build/hf-trajectories-without-glm-uploaded.json`。
本地备份、删除计划、公开包和回执保存在 `.build/`，不会随官网发布。
脚本不会 add、commit 或 push 网站仓库，也不会删除本机原始评测记录。

HF 删除作用于当前版本，历史提交保留旧文件，不重写仓库历史。

## 历史记录：2026-10-31 两题撤销（已执行）

2026-10-31 撤销 `deletion-resilient-vector-search` 和
`resource-bounded-multivector-search`。当时更新为 47 题（24 CPU、23 GPU）、4 个模型、
188 份结果。两题不按零分计入，榜单、tokens 和时长均按剩余结果重新汇总。

以下为当时使用的命令，不用于本次模型下架：

```bash
python scripts/prune_hf_tasks.py          # 离线核对并列出删除范围
python scripts/prune_hf_tasks.py --apply  # 执行 HF 更新、校验并更新本地官网
```

已准备好 `.build/hf-trajectories-47/` 公开包和
`.build/hf-task-removal-2026-10-31.json` 精确操作清单，不需要重新导出。
脚本复用已有 HF 登录，或读取 `HF_TOKEN`。缺少依赖时运行
`python -m pip install -r scripts/requirements-hf.txt`；尚未登录时运行 `hf auth login`。

本次从 `releases/2026-10-30-3090361873/trials/` 删除上述两题对应的 8 个目录，
共 1,069 个文件、约 45.97 MiB。仅上传 README、该 release 的 `snapshot.json`
和 `publication.json.gz` 三个文件，其余 188 份轨迹逐字节保留，不重复上传。
删除与摘要更新放在同一次 HF commit 中，并限制父提交为原先验证过的
`966567209b031769d3fa024c42e43ac461739231`，避免覆盖并发修改。

中断后重跑相同命令即可：如果提交已成功，脚本核对新摘要及删除结果后继续
远端哈希、匿名下载和 CORS 校验，不重复删除。只有校验成功才改写
`content/leaderboard/storage.json` 并生成 194 个官网页面。
执行回执保存在 `.build/hf-task-removal-2026-10-31.applied.json` 和
`.build/hf-trajectories-47-uploaded.json`。不会执行网站仓库的 add、commit 或 push。

脚本执行前，本地页面使用已过滤的公开包预览，`--production` 检查会拒绝这个
尚未发布的配置。执行成功后改为固定的新 HF SHA，届时运行：

```bash
python scripts/build_leaderboard.py --production --check
```

删除针对 HF 当前版本；HF 的历史提交仍会保留旧文件。本脚本不重写仓库历史。
旧官网在本地变更发布之前仍会引用原来的固定 SHA。

## 旧版追加发布流程（不会清除旧轨迹）

以下用于后续新增评测的完整发布。先按下一节准备与本地结果匹配的新包，再运行：

```bash
python -m pip install -r scripts/requirements-hf.txt
hf auth login
python scripts/upload_hf_release.py --package .build/hf-trajectories-next
python scripts/upload_hf_release.py --package .build/hf-trajectories-next --upload
```

已经登录过 HF 时可省略 `hf auth login`。也支持通过环境变量 `HF_TOKEN` 提供
对目标 dataset 的写权限；不要把 token 写进脚本或网页。

不加 `--upload` 时只做离线检查，既不上传也不访问 HF。用 `--package` 指定
本次准备的包，避免误用早期的 `.build/hf-trajectories/`。文件较多，上传使用可恢复的 `upload_large_folder`；
中断后对同一份未修改的发布包重跑相同命令即可。默认 4 个 worker，可用
`--workers 2` 调低并发。脚本保留既有 release，不删除远端文件。

上传成功后脚本会自动：

1. 最后提交发布清单，取得实际上传 commit 的完整 SHA。
2. 按这个 SHA 校验所有远端文件的大小及 Git/LFS 内容哈希。
3. 匿名读取真实 JSON、较大 JSON 和 gzip，检查下载哈希及官网 Origin 的 CORS。
4. 写入 `content/leaderboard/storage.json`，将所有数据 URL 固定到该 commit。
5. 生成对应的官网页面，保存上传包旁的 `*-uploaded.json` 回执。

这一步只更新本地网站文件，不会 git commit、push 或部署官网。之后检查：

```bash
python scripts/build_leaderboard.py --production --check
```

上传完成但网络校验中断时，也可用上传日志中的实际 SHA 继续校验并接入官网，
无需再次上传：

```bash
python scripts/upload_hf_release.py --package .build/hf-trajectories-next --verify-revision FULL_40_CHARACTER_COMMIT_SHA
```

## 旧归档格式的重建流程（历史参考）

以下仅适用于旧版带 `traj-analysis/leaderboard-data` 的归档。当前归档使用上文的新导入器。历史命令：

```bash
python scripts/import_results.py --jobs /path/to/Search-SWE/jobs
python scripts/leaderboard_costs.py --usage /path/to/Search-SWE/jobs/traj-analysis/leaderboard-data/usage.json
python scripts/prepare_hf_release.py \
  --jobs /path/to/Search-SWE/jobs \
  --output .build/hf-trajectories-next
python scripts/prepare_hf_release.py --check --output .build/hf-trajectories-next
python scripts/upload_hf_release.py --package .build/hf-trajectories-next --upload
```

导出只使用 `final-trajectories/INDEX.csv` 的最终选择，并应用网站的 `selection.json`
模型排除规则，核对分析、轨迹和最终 reward 的源哈希。不会写入原始 jobs、重新解题或重新评分。

发布包结构：

```text
README.md
publication.json.gz                 # 完整文件清单、字节数、SHA-256、Git blob hash
releases/<date-selection-hash>/
  snapshot.json                     # 当前选中 trial 的评分、用量、模型及来源摘要
  trials/<trial-id>/
    manifest.json                   # 轨迹步骤索引
    steps-*.json                    # 阅读分片
    calls-*.json / text-*.json       # 超长内容和并行调用分片（按需存在）
    search.json
    trajectory.json.gz              # 公开 ATIF 下载
    evaluation.json
    files/index.json                # 各 tab 的目录树
    files/*.json / *.txt.gz         # 文件预览分片及对应完整文本下载
```

压缩清单和轨迹下载使用仓库已有的 `*.gz` LFS 规则。普通阅读分片仍是可直接
`response.json()` 的 JSON。源评测变化会生成新的 snapshot/entry URL；仅调整网站模型
选择时，snapshot URL 更新，保留模型的 entry/trial URL 不变。下架任务或模型时，
同步清理旧生成页面和包含已下架结果的公开 snapshot。

## 路径与公开数据边界

宿主机的绝对路径在分片之前转换成 `${BENCHMARK_ROOT}`、`${EVAL_ROOT}`、
`${WORKSPACE_ROOT}`、`${USER_HOME}` 等通用别名。别名表示来源环境，不是文件下载链接。
`/app`、`/tests`、`/logs`、`/tmp` 和任务数据路径保留，以便理解原始执行命令。
预览、搜索内容、原生会话日志、配置、异常和 gzip 下载使用同一套转换规则。

凭据模式、结构化凭据及环境变量值会被脱敏。只导出最终选择的轨迹和原有
允许预览的文本证据；隐藏文件、符号链接、完整 jobs、模型权重、索引及大型
二进制文件不上传。文件树中仍可列出不可预览产物的名称与大小。

源 SHA-256 仍对应未经修改的原始记录；公开文件哈希对应清理后的内容。
保持 HF 仓库现有的 `cc-by-nc-sa-4.0` 声明，第三方文件保留自身许可说明。

## 预览、验证和正式构建

上传前 `storage.json` 使用 `preview`，本地 7788 从准备好的公开发布包读取，
方便检查路径和排版。`--production` 会拒绝 `local`、`preview`、`main`、短 SHA
以及与本地结果摘要不匹配的配置，避免生成尚不存在或版本不固定的官网链接。
上传并验证成功后脚本自动切换到 `huggingface`。

```bash
PYTHONPATH=scripts python -m unittest \
  scripts/test_publication.py scripts/test_leaderboard.py scripts/test_trial_files.py
HF_PACKAGE=.build/hf-trajectories-without-glm NODE_PATH=/path/to/playwright/node_modules node scripts/test_hf_browser.cjs
```

浏览器检查使用另一个真实 HTTP origin 提供公开发布包，验证匿名跨域加载、
下载一致性、整个轨迹连续阅读、目录树、搜索、失败重试及手机布局。它会暂时
重建本地页面并在结束后恢复默认配置。真实 HF 文件的远端哈希和 CORS 检查由
上传脚本在上传完成后执行；上传前无法验证尚不存在的远端文件。

上传机制参考 [HF 大目录上传文档](https://huggingface.co/docs/huggingface_hub/guides/upload)。
