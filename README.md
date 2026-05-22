# AI 开发者反馈分类与摘要工具

这是一个基于通义千问 API 搭建的 AI Developer Feedback Analyzer Demo。

它可以帮助开发者运营、Developer Relations、产品运营团队快速分析开发者反馈，识别反馈类别、优先级、情绪倾向，并生成产品优化建议和运营动作建议。

## 功能

- 开发者反馈自动分类
- 优先级判断
- 情绪识别
- 开发者真实需求提炼
- 产品优化建议生成
- 运营动作建议生成
- 分析结果 CSV 下载

## 使用场景

- GitHub Issue 反馈分析
- Discord / Reddit 社区反馈整理
- 开发者活动问卷分析
- API / SDK / 文档问题归因
- AI 产品体验反馈总结

## 技术栈

- Python
- Streamlit
- 通义千问 API / Qwen API
- OpenAI-compatible API
- Pandas

## 本地运行

安装依赖：

```bash
pip3 install -r requirements.txt
```

创建 `.env` 文件：

```txt
DASHSCOPE_API_KEY=your_api_key_here
```

启动应用：

```bash
streamlit run app.py
```

## 项目价值

这个 Demo 展示了如何将大模型能力应用到 AI 开发者运营场景中，帮助团队更高效地理解开发者需求，建立反馈分析和产品优化闭环。
