import json
import os
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
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
    page_title="AI Developer Feedback Ops",
    page_icon="AI",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #111827;
        --muted: #667085;
        --line: #e5e7eb;
        --panel: #ffffff;
        --soft: #f7f8fb;
        --deep: #071527;
        --deep-2: #0f2747;
        --blue: #1f6feb;
        --cyan: #22d3ee;
        --green: #059669;
        --amber: #d97706;
        --red: #dc2626;
    }
    .stApp {
        background:
            radial-gradient(circle at 15% 8%, rgba(34, 211, 238, 0.12), transparent 26%),
            linear-gradient(180deg, #f4f7fb 0%, #ffffff 42%);
    }
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0.85rem;
    }
    .hero {
        border: 1px solid rgba(255, 255, 255, 0.12);
        background:
            radial-gradient(circle at 78% 12%, rgba(34, 211, 238, 0.24), transparent 25%),
            linear-gradient(135deg, var(--deep) 0%, var(--deep-2) 55%, #123b68 100%);
        padding: 30px 32px;
        border-radius: 8px;
        margin-bottom: 14px;
        box-shadow: 0 18px 44px rgba(7, 21, 39, 0.16);
    }
    .hero h1 {
        color: #ffffff;
        font-size: 34px;
        line-height: 1.2;
        margin: 0 0 8px 0;
        letter-spacing: 0;
    }
    .hero p {
        color: #c9d7e8;
        font-size: 15px;
        margin: 0;
        max-width: 900px;
    }
    .eyebrow {
        color: #8ddcff;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0;
        margin-bottom: 10px;
    }
    .hero-meta {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 18px;
    }
    .hero-pill {
        border: 1px solid rgba(141, 220, 255, 0.32);
        color: #e6f6ff;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 999px;
        padding: 7px 11px;
        font-size: 13px;
        font-weight: 650;
    }
    .input-panel {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.9);
        padding: 16px 18px;
        min-height: 144px;
    }
    .panel-title {
        color: var(--ink);
        font-size: 15px;
        font-weight: 750;
        margin-bottom: 4px;
    }
    .panel-desc {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0f2747 0%, #1f6feb 100%);
        color: white;
        border: 0;
        border-radius: 8px;
        font-weight: 750;
        min-height: 44px;
        padding-left: 22px;
        padding-right: 22px;
    }
    div.stButton > button:first-child:hover {
        color: white;
        border: 0;
        box-shadow: 0 10px 24px rgba(31, 111, 235, 0.22);
    }
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--ink);
        margin: 10px 0 4px 0;
    }
    .section-note {
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 6px;
    }
    .metric-card {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 16px;
        background: var(--panel);
        min-height: 112px;
    }
    .metric-label {
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 8px;
    }
    .metric-value {
        color: var(--ink);
        font-size: 30px;
        line-height: 1;
        font-weight: 750;
        margin-bottom: 8px;
    }
    .metric-sub {
        color: var(--muted);
        font-size: 12px;
    }
    .insight-card {
        border: 1px solid var(--line);
        border-left: 4px solid var(--blue);
        border-radius: 8px;
        padding: 16px 18px;
        background: var(--panel);
        min-height: 116px;
    }
    .insight-card strong {
        color: var(--ink);
    }
    .insight-card p {
        color: var(--muted);
        margin: 8px 0 0 0;
        font-size: 14px;
    }
    .tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 6px;
    }
    .tag {
        display: inline-flex;
        align-items: center;
        border: 1px solid #dbeafe;
        color: #1d4ed8;
        background: #eff6ff;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 13px;
        font-weight: 600;
    }
    .risk-high {
        border-color: #fecaca;
        background: #fef2f2;
        color: #b91c1c;
    }
    .risk-mid {
        border-color: #fed7aa;
        background: #fff7ed;
        color: #c2410c;
    }
    .risk-low {
        border-color: #bbf7d0;
        background: #f0fdf4;
        color: #15803d;
    }
    .action-box {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 14px 16px;
        background: var(--soft);
        min-height: 100px;
        margin-bottom: 10px;
    }
    .action-box b {
        color: var(--ink);
    }
    .action-box span {
        color: var(--muted);
        display: block;
        margin-top: 6px;
        line-height: 1.55;
    }
    .feedback-card {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 14px 16px;
        background: #ffffff;
        margin-bottom: 10px;
    }
    .feedback-card .quote {
        color: var(--ink);
        font-weight: 650;
        margin-bottom: 8px;
    }
    .feedback-card .need {
        color: var(--muted);
        font-size: 14px;
        margin-top: 8px;
    }
    .small-muted {
        color: var(--muted);
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">DEVELOPER FEEDBACK OPS / LLM PLATFORM</div>
        <h1>大模型开发者反馈运营看板</h1>
        <p>面向 DeepSeek API、AI Agent 平台和开发者社区，将零散反馈转化为问题分布、风险优先级、产品优化建议和运营周报。</p>
        <div class="hero-meta">
            <span class="hero-pill">API 使用反馈</span>
            <span class="hero-pill">Token 与计费问题</span>
            <span class="hero-pill">模型体验洞察</span>
            <span class="hero-pill">产品优化闭环</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

sample_feedback = """DeepSeek API 的鉴权文档不够清楚，我不确定 Authorization Bearer token 应该放在哪一层配置里。
我按照 OpenAI 兼容接口迁移代码后，messages 格式可以跑通，但 function calling 的示例不完整。
调用 deepseek-chat 时偶尔返回 429，希望文档明确限流规则和重试建议。
流式输出的示例只有 Python，希望补充 JavaScript/Node.js 的 SSE 示例。
Token 计费说明不够直观，开发者很难预估一次长上下文调用的大概成本。
控制台错误码提示太笼统，401、402、429、500 的排查路径应该分开写。
希望提供一个 RAG + DeepSeek API 的完整示例项目，最好能直接部署运行。
模型响应速度在晚高峰明显变慢，批量生成报告时等待时间较长。
企业客户希望支持团队级 API Key 管理和用量看板，现在个人 Key 不方便协作。
上下文长度、最大输出 token 和截断规则说明不够清楚，长文档总结时经常超限。
希望官方提供 LangChain、LlamaIndex、Dify 等主流框架的接入教程。
API 余额不足时只返回失败，建议提前预警并提供余额、消耗和调用趋势看板。
开发者社区里重复问题很多，希望官方维护一个高频问题 FAQ 和最佳实践合集。
模型更新日志不够显眼，开发者不知道版本变化会不会影响线上应用效果。"""

st.markdown('<div class="section-title">配置</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-note">选择反馈来源和分析模型，默认样例模拟开发者调用 DeepSeek 模型接口时的真实问题。</div>',
    unsafe_allow_html=True,
)

config_col, input_col = st.columns([0.34, 0.66])

with config_col:
    st.markdown(
        """
        <div class="input-panel">
            <div class="panel-title">数据源与模型</div>
            <div class="panel-desc">适用于 API 文档反馈、技术社群答疑、GitHub issue、活动问卷和企业客户工单。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    input_mode = st.radio(
        "反馈输入方式",
        ["手动输入", "上传 CSV"],
        horizontal=True,
    )
    model_name = st.selectbox("分析模型", ["qwen-plus", "qwen-turbo"], index=0)

feedback_text = ""

with input_col:
    if input_mode == "手动输入":
        feedback_text = st.text_area(
            "开发者反馈样本",
            value=sample_feedback,
            height=330,
            help="每行一条反馈。当前样例以开发者调用 DeepSeek API 的典型问题为场景。",
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


def get_count(counts, label):
    return int(counts.get(label, 0))


def pct(part, total):
    if total == 0:
        return "0%"
    return f"{part / total:.0%}"


def to_html_list(items):
    return "".join(f"<div class='action-box'><b>建议 {index}</b><span>{item}</span></div>" for index, item in enumerate(items, 1))


def build_bar_html(counts, total, color):
    if total == 0:
        return "<div class='report-muted'>暂无数据</div>"

    rows = []
    for label, value in counts.items():
        width = max(6, round(value / total * 100))
        rows.append(
            f"""
            <div class="report-bar-row">
                <div class="report-bar-label">{escape(str(label))}</div>
                <div class="report-bar-track">
                    <div class="report-bar-fill" style="width:{width}%; background:{color};"></div>
                </div>
                <div class="report-bar-value">{int(value)} / {value / total:.0%}</div>
            </div>
            """
        )
    return "".join(rows)


def build_report_html(result, df, category_counts, priority_counts, sentiment_counts):
    total_count = len(df)
    high_count = get_count(priority_counts, "高")
    negative_count = get_count(sentiment_counts, "负向")
    top_category = category_counts.index[0] if not category_counts.empty else "暂无"
    keywords = "".join(f"<span>{escape(str(keyword))}</span>" for keyword in result["top_keywords"])
    product_items = "".join(f"<li>{escape(item)}</li>" for item in result["product_suggestions"])
    operation_items = "".join(f"<li>{escape(item)}</li>" for item in result["operation_suggestions"])
    feedback_items = "".join(
        f"""
        <tr>
            <td>{escape(item.get("category", ""))}</td>
            <td>{escape(item.get("priority", ""))}</td>
            <td>{escape(item.get("sentiment", ""))}</td>
            <td>{escape(item.get("developer_need", ""))}</td>
            <td>{escape(item.get("suggested_action", ""))}</td>
        </tr>
        """
        for item in result["feedback_items"][:8]
    )

    return f"""
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>大模型开发者反馈运营周报</title>
<style>
body {{
    margin: 0;
    background: #f4f7fb;
    color: #111827;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}}
.report {{
    width: 960px;
    margin: 28px auto;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    overflow: hidden;
}}
.report-hero {{
    background: linear-gradient(135deg, #071527 0%, #0f2747 58%, #123b68 100%);
    color: white;
    padding: 30px 34px;
}}
.report-hero small {{
    color: #8ddcff;
    font-weight: 700;
}}
.report-hero h1 {{
    margin: 10px 0 8px;
    font-size: 30px;
}}
.report-hero p {{
    margin: 0;
    color: #c9d7e8;
}}
.report-body {{
    padding: 28px 34px 34px;
}}
.report-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}}
.report-metric {{
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 14px;
    background: #f9fafb;
}}
.report-metric label {{
    display: block;
    color: #667085;
    font-size: 12px;
    margin-bottom: 8px;
}}
.report-metric b {{
    display: block;
    font-size: 26px;
    line-height: 1;
}}
.report-section {{
    margin-top: 26px;
}}
.report-section h2 {{
    font-size: 18px;
    margin: 0 0 12px;
}}
.report-summary {{
    border-left: 4px solid #1f6feb;
    background: #f5f8ff;
    padding: 14px 16px;
    border-radius: 8px;
    color: #344054;
    line-height: 1.7;
}}
.report-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}}
.report-tags span {{
    border: 1px solid #bfdbfe;
    background: #eff6ff;
    color: #1d4ed8;
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 13px;
    font-weight: 650;
}}
.report-chart-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}}
.report-chart {{
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
}}
.report-bar-row {{
    display: grid;
    grid-template-columns: 92px 1fr 72px;
    gap: 10px;
    align-items: center;
    margin: 12px 0;
    font-size: 13px;
}}
.report-bar-label {{
    color: #344054;
}}
.report-bar-track {{
    height: 10px;
    background: #eef2f7;
    border-radius: 999px;
    overflow: hidden;
}}
.report-bar-fill {{
    height: 10px;
    border-radius: 999px;
}}
.report-bar-value {{
    color: #667085;
    text-align: right;
}}
.report-two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}}
.report-card {{
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    background: #ffffff;
}}
.report-card ul {{
    margin: 0;
    padding-left: 18px;
    line-height: 1.7;
    color: #344054;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}}
th, td {{
    border-bottom: 1px solid #e5e7eb;
    padding: 9px 8px;
    text-align: left;
    vertical-align: top;
}}
th {{
    background: #f9fafb;
    color: #344054;
}}
.report-muted {{
    color: #667085;
    font-size: 13px;
}}
@media print {{
    body {{ background: white; }}
    .report {{ width: auto; margin: 0; border: 0; }}
}}
</style>
</head>
<body>
<main class="report">
    <section class="report-hero">
        <small>DEVELOPER FEEDBACK OPS REPORT</small>
        <h1>大模型开发者反馈运营周报</h1>
        <p>面向 DeepSeek API / 大模型开放平台，识别开发者痛点、平台风险与下一步优化动作。</p>
    </section>
    <section class="report-body">
        <div class="report-grid">
            <div class="report-metric"><label>反馈总量</label><b>{total_count}</b></div>
            <div class="report-metric"><label>高优先级</label><b>{high_count}</b></div>
            <div class="report-metric"><label>负向反馈</label><b>{negative_count}</b></div>
            <div class="report-metric"><label>首要问题</label><b>{escape(str(top_category))}</b></div>
        </div>
        <section class="report-section">
            <h2>核心摘要</h2>
            <div class="report-summary">{escape(result["summary"])}</div>
            <div class="report-tags">{keywords}</div>
        </section>
        <section class="report-section">
            <h2>问题分布图</h2>
            <div class="report-chart-grid">
                <div class="report-chart">
                    <b>问题类型分布</b>
                    {build_bar_html(category_counts, total_count, "#1f6feb")}
                </div>
                <div class="report-chart">
                    <b>优先级分布</b>
                    {build_bar_html(priority_counts, total_count, "#0f2747")}
                </div>
            </div>
        </section>
        <section class="report-section">
            <h2>建议动作</h2>
            <div class="report-two-col">
                <div class="report-card"><b>产品优化建议</b><ul>{product_items}</ul></div>
                <div class="report-card"><b>运营动作建议</b><ul>{operation_items}</ul></div>
            </div>
        </section>
        <section class="report-section">
            <h2>重点反馈明细</h2>
            <table>
                <thead>
                    <tr><th>类型</th><th>优先级</th><th>情绪</th><th>真实需求</th><th>建议动作</th></tr>
                </thead>
                <tbody>{feedback_items}</tbody>
            </table>
        </section>
    </section>
</main>
</body>
</html>
"""


def render_metric(label, value, subtext):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tags(tags):
    tag_html = "".join(f"<span class='tag'>{tag}</span>" for tag in tags)
    st.markdown(f"<div class='tag-row'>{tag_html}</div>", unsafe_allow_html=True)


def render_feedback_card(item):
    priority_class = {
        "高": "risk-high",
        "中": "risk-mid",
        "低": "risk-low",
    }.get(item.get("priority", ""), "")
    st.markdown(
        f"""
        <div class="feedback-card">
            <div class="quote">{item.get("original_feedback", "")}</div>
            <div class="tag-row">
                <span class="tag">{item.get("category", "其他")}</span>
                <span class="tag {priority_class}">优先级：{item.get("priority", "")}</span>
                <span class="tag">情绪：{item.get("sentiment", "")}</span>
            </div>
            <div class="need"><b>开发者真实需求：</b>{item.get("developer_need", "")}</div>
            <div class="need"><b>建议动作：</b>{item.get("suggested_action", "")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(result):
    df = pd.DataFrame(result["feedback_items"])
    category_counts = df["category"].value_counts()
    priority_counts = df["priority"].value_counts()
    sentiment_counts = df["sentiment"].value_counts()
    total_count = len(df)
    high_count = get_count(priority_counts, "高")
    negative_count = get_count(sentiment_counts, "负向")
    top_category = category_counts.index[0] if not category_counts.empty else "暂无"
    weekly_report = build_weekly_report(result, category_counts, priority_counts)

    st.markdown('<div class="section-title">运营总览</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">从反馈规模、风险优先级、情绪状态和主要问题类型判断本批反馈的处理重点。</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("反馈总量", total_count, "本批有效开发者反馈")
    with col2:
        render_metric("高优先级", high_count, f"占比 {pct(high_count, total_count)}")
    with col3:
        render_metric("负向反馈", negative_count, f"占比 {pct(negative_count, total_count)}")
    with col4:
        render_metric("首要问题", top_category, "当前最集中的反馈类型")

    st.markdown('<div class="section-title">AI 摘要与关键词</div>', unsafe_allow_html=True)
    insight_col, tag_col = st.columns([2, 1])
    with insight_col:
        st.markdown(
            f"""
            <div class="insight-card">
                <strong>核心判断</strong>
                <p>{result["summary"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tag_col:
        st.markdown("**高频关键词**")
        render_tags(result["top_keywords"])

    tab_overview, tab_actions, tab_details, tab_report = st.tabs(
        ["问题洞察", "行动计划", "反馈明细", "周报与导出"]
    )

    with tab_overview:
        st.markdown('<div class="section-title">问题分布</div>', unsafe_allow_html=True)
        chart_col1, chart_col2, chart_col3 = st.columns(3)
        with chart_col1:
            st.write("问题类型")
            st.bar_chart(category_counts)
        with chart_col2:
            st.write("优先级")
            st.bar_chart(priority_counts)
        with chart_col3:
            st.write("情绪分布")
            st.bar_chart(sentiment_counts)

        st.markdown('<div class="section-title">运营优先级矩阵</div>', unsafe_allow_html=True)
        matrix = pd.crosstab(df["category"], df["priority"])
        for column in ["高", "中", "低"]:
            if column not in matrix.columns:
                matrix[column] = 0
        matrix = matrix[["高", "中", "低"]]
        st.dataframe(matrix, use_container_width=True)

    with tab_actions:
        product_col, ops_col = st.columns(2)
        with product_col:
            st.markdown('<div class="section-title">产品优化建议</div>', unsafe_allow_html=True)
            st.markdown(to_html_list(result["product_suggestions"]), unsafe_allow_html=True)
        with ops_col:
            st.markdown('<div class="section-title">运营动作建议</div>', unsafe_allow_html=True)
            st.markdown(to_html_list(result["operation_suggestions"]), unsafe_allow_html=True)

    with tab_details:
        st.markdown('<div class="section-title">逐条反馈卡片</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-note">适合在面试展示时说明：每条反馈都会被转化为分类、优先级、真实需求和下一步动作。</div>', unsafe_allow_html=True)
        for item in result["feedback_items"]:
            render_feedback_card(item)

        with st.expander("查看结构化明细表"):
            st.dataframe(df, use_container_width=True)

    with tab_report:
        st.markdown('<div class="section-title">图文运营周报</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-note">报告包含核心指标、问题分布图、产品建议、运营动作和重点反馈明细，更适合汇报与转发。</div>',
            unsafe_allow_html=True,
        )
        report_html = build_report_html(
            result,
            df,
            category_counts,
            priority_counts,
            sentiment_counts,
        )
        st.download_button(
            label="下载图文运营周报 HTML 文档",
            data=report_html.encode("utf-8"),
            file_name="developer_feedback_ops_report.html",
            mime="text/html",
        )

        with st.expander("查看文字版周报草稿"):
            st.text_area("可复制给产品、运营或社区团队：", value=weekly_report, height=220)

        with st.expander("预览图文报告内容"):
            components.html(report_html, height=760, scrolling=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="下载结构化反馈 CSV",
            data=csv,
            file_name="developer_feedback_analysis.csv",
            mime="text/csv",
        )


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
                st.session_state["analysis_result"] = result
                render_dashboard(result)

            except json.JSONDecodeError:
                st.error("模型返回结果不是标准 JSON。可以再点击一次，或减少输入内容后重试。")
                st.text(result_text)
            except Exception as error:
                st.error(f"分析失败：{error}")
elif "analysis_result" in st.session_state:
    render_dashboard(st.session_state["analysis_result"])
