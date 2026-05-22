import json
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    ),
)

st.set_page_config(
    page_title="AI 开发者反馈分析工具",
    page_icon="AI",
    layout="wide",
)

st.title("AI 开发者反馈分类与摘要工具")
st.caption("基于通义千问 API，对开发者反馈进行分类、优先级判断、情绪识别与摘要生成。")

sample_feedback = """API 文档里的鉴权说明不够清楚，我照着做一直报 401。
希望 SDK 能提供 JavaScript 示例，现在只有 Python 示例。
模型响应速度有点慢，批量处理反馈时等待时间比较长。
控制台的错误提示太笼统，不知道到底是参数错了还是额度不够。
如果能提供一个完整的 Agent Demo 项目，会更容易上手。"""

input_mode = st.radio(
    "选择反馈输入方式",
    ["手动输入", "上传 CSV"],
    horizontal=True,
)

feedback_text = ""

if input_mode == "手动输入":
    feedback_text = st.text_area(
        "请输入开发者反馈，每行一条：",
        value=sample_feedback,
        height=220,
    )
else:
    uploaded_file = st.file_uploader(
        "上传 CSV 文件",
        type=["csv"],
        help="CSV 文件中需要有一列开发者反馈内容，例如 feedback、content、text、反馈内容。",
    )

    if uploaded_file is not None:
        uploaded_df = pd.read_csv(uploaded_file)
        st.write("已读取文件预览：")
        st.dataframe(uploaded_df.head(10), use_container_width=True)

        column_options = list(uploaded_df.columns)
        default_column = next(
            (
                column
                for column in ["feedback", "content", "text", "反馈内容", "开发者反馈"]
                if column in column_options
            ),
            column_options[0],
        )
        feedback_column = st.selectbox(
            "请选择包含反馈内容的列",
            column_options,
            index=column_options.index(default_column),
        )
        feedback_list = uploaded_df[feedback_column].dropna().astype(str).tolist()
        feedback_text = "\n".join(feedback_list)
        st.caption(f"本次将分析 {len(feedback_list)} 条反馈。")
    else:
        st.info("请上传一个 CSV 文件，或切换到手动输入模式。")

model_name = st.selectbox(
    "选择模型",
    ["qwen-plus", "qwen-turbo"],
    index=0,
)

analyze_button = st.button("开始分析", type="primary")


def build_weekly_report(result, category_counts, priority_counts):
    top_category = category_counts.index[0] if not category_counts.empty else "暂无"
    high_priority_count = int(priority_counts.get("高", 0))
    keywords = "、".join(result["top_keywords"])
    product_actions = "；".join(result["product_suggestions"])
    operation_actions = "；".join(result["operation_suggestions"])

    return f"""本周开发者反馈摘要：
本批反馈主要集中在「{top_category}」，其中高优先级问题 {high_priority_count} 条。开发者关注的核心关键词包括：{keywords}。

产品侧建议：
{product_actions}

运营侧建议：
{operation_actions}

整体判断：
{result["summary"]}"""


def analyze_feedback(input_text, selected_model):
    prompt = f"""
你是一名资深 AI 开发者运营专家，负责分析开发者社区、GitHub issue、Discord、Reddit、技术社群中的用户反馈。

请分析下面这批开发者反馈，并输出严格 JSON，不要输出 Markdown，不要输出多余解释。

反馈内容：
{input_text}

请按照以下 JSON 格式输出：
{{
  "summary": "用 100 字以内总结这批反馈的核心问题",
  "feedback_items": [
    {{
      "original_feedback": "原始反馈",
      "category": "问题类型，只能从 文档问题/API问题/性能问题/功能建议/错误提示/示例代码/其他 中选择",
      "priority": "优先级，只能从 高/中/低 中选择",
      "sentiment": "情绪，只能从 正向/中性/负向 中选择",
      "developer_need": "开发者真实需求",
      "suggested_action": "建议运营或产品采取的动作"
    }}
  ],
  "top_keywords": ["关键词1", "关键词2", "关键词3"],
  "product_suggestions": ["产品建议1", "产品建议2", "产品建议3"],
  "operation_suggestions": ["运营建议1", "运营建议2", "运营建议3"]
}}
"""

    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的 AI 开发者运营分析助手，擅长结构化分析开发者反馈。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


if analyze_button:
    if not os.getenv("DASHSCOPE_API_KEY"):
        st.error("没有找到 DASHSCOPE_API_KEY。请先在 .env 文件中配置你的通义千问 API Key。")
    elif not feedback_text.strip():
        st.warning("请先输入开发者反馈。")
    else:
        with st.spinner("AI 正在分析开发者反馈..."):
            try:
                result_text = analyze_feedback(feedback_text, model_name)
                result = json.loads(result_text)

                st.subheader("反馈摘要")
                st.write(result["summary"])

                st.subheader("关键词")
                st.write("、".join(result["top_keywords"]))

                st.subheader("逐条反馈分析")
                df = pd.DataFrame(result["feedback_items"])
                st.dataframe(df, use_container_width=True)

                st.subheader("问题分布")
                category_counts = df["category"].value_counts()
                priority_counts = df["priority"].value_counts()

                col1, col2 = st.columns(2)
                with col1:
                    st.write("问题类型统计")
                    st.bar_chart(category_counts)
                with col2:
                    st.write("优先级统计")
                    st.bar_chart(priority_counts)

                st.subheader("产品优化建议")
                for item in result["product_suggestions"]:
                    st.write(f"- {item}")

                st.subheader("运营动作建议")
                for item in result["operation_suggestions"]:
                    st.write(f"- {item}")

                st.subheader("运营周报")
                weekly_report = build_weekly_report(result, category_counts, priority_counts)
                st.text_area(
                    "可复制给产品、运营或社区团队的周报草稿：",
                    value=weekly_report,
                    height=260,
                )

                csv = df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="下载分析结果 CSV",
                    data=csv,
                    file_name="developer_feedback_analysis.csv",
                    mime="text/csv",
                )

            except json.JSONDecodeError:
                st.error("模型返回结果不是标准 JSON。可以再点击一次，或减少输入内容后重试。")
                st.text(result_text)
            except Exception as error:
                st.error(f"分析失败：{error}")
