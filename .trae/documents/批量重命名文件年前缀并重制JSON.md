## 目标
- 将 `d:\github\salary\lazyblog\files` 中以 `23`/`24` 开头的 Markdown 文件批量重命名：`23YYYY` → `2023YYYY`，`24YYYY` → `2024YYYY`，保留后续文件名不变。
- 重跑 JSON 生成，得到与新文件名一致且按日期倒序的 `posts.json`。

## 实施步骤
1. 编写脚本 `lazyblog/scripts/rename_year_prefix.py`：
   - 扫描 `files` 目录，匹配 `^23\d{4}` 或 `^24\d{4}` 开头的文件名；生成目标文件名为 `2023`/`2024` + 原后四位 + 其余部分。
   - 若目标文件已存在则跳过并打印记录，避免覆盖。
   - 执行安全重命名（`Path.rename`）。
2. 运行重命名脚本并输出变更列表，便于核对。
3. 重新运行 `lazyblog/scripts/generate_posts_json.py`：
   - 解析前缀日期（支持 8 位/6 位），输出 `date` 为 `YYYY-MM-DD`。
   - 按 `date` 倒序生成 `d:\github\salary\lazyblog\data\posts.json`。
4. 验证：
   - 抽样查看 `posts.json` 顶部若干条，确认 `2025`/`2024`/`2023` 排序与日期正确。
   - 打开站点查看列表顺序与阅读内容。

## 说明
- 仅修改文件名，不改文件内容；避免命名冲突导致覆盖。
- 若后续需要把 25 开头统一转为 `2025`，脚本可轻松扩展。