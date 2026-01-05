## DeepSeek 配置（OpenAI 兼容）

本项目通过环境变量读取 DeepSeek 配置（已在 `evaluator.py` 里调用 `load_dotenv()`）。

### 1) 在 `ai_answer_evaluator/` 目录新建 `.env`

> 注意：本仓库的忽略规则可能禁止提交/创建 `.env*` 示例文件；你只需要在本机创建即可。

内容示例：

```env
DEEPSEEK_API_KEY=你的deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 2) 运行

确保 Code Runner 使用虚拟环境解释器（你当前已配置为 `E:\test_demo\.venv\Scripts\python.exe`），然后直接运行 `ai_answer_evaluator/evaluator.py`。


