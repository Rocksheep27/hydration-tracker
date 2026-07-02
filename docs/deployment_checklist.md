# Deployment Checklist

## 发布前

- 在当前实际使用环境导出 JSON 备份。
- 确认 `git status` 干净。
- 运行 `python3 -m unittest discover tests`。
- 确认 localStorage key 仍为 `hydration_tracker_v3_records`。
- 确认 `schema_version` 仍为 `1`。
- 确认 JSON 导入导出可正常使用。

## 推送后

- 检查 GitHub Actions workflow 是否成功。
- 打开正式网址确认页面可以加载。
- 在 iPhone Safari 中测试正式网址。
- 从主屏幕打开并确认基本使用正常。

## 发布后验证

- 测试添加记录。
- 测试历史记录查看。
- 测试指定日期补录。
- 测试历史单条删除。
- 测试清空指定日期。
- 测试 JSON 导出和导入。
- 测试离线启动。
- 测试 Service Worker 更新。
