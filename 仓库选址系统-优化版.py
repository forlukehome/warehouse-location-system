"""
仓库选址教学系统 v2.0 — 深度优化版
Warehouse Location Selection Teaching System
优化特性：迭代重心法、敏感度分析、蒙特卡洛仿真、多方案对比、学习追踪等
"""

import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import time
import io
import base64
import random

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="仓库选址教学系统 v2.0",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Session State 初始化 ====================
DEFAULTS = {
    'learning_progress': {},          # {module: score}
    'quiz_history': [],               # [{date, score, total}]
    'exercises_completed': 0,
    'simulation_data': None,
    'quiz_state': {},
    'visited_pages': set(),
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ==================== 自定义CSS ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1565C0;
        border-left: 5px solid #1E88E5;
        padding-left: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
        margin: 0.8rem 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF9800;
        margin: 0.8rem 0;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 0.8rem 0;
    }
    .danger-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #F44336;
        margin: 0.8rem 0;
    }
    .step-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 0.8rem 0;
        border: 1px solid #e0e0e0;
    }
    .highlight-num {
        font-size: 2rem;
        font-weight: bold;
        color: #1565C0;
    }
    .progress-bar-container {
        background: #e0e0e0;
        border-radius: 10px;
        height: 20px;
        margin: 0.5rem 0;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 10px;
        height: 100%;
        transition: width 0.5s ease;
    }
    div[data-testid="stExpander"] details summary {
        background-color: #f0f4ff;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("📚 教学导航")
    st.markdown("---")
    page = st.radio(
        "选择学习模块",
        ["🏠 首页", "📖 理论知识", "🧮 计算工具", "📊 敏感度分析",
         "📋 多方案对比", "📊 案例分析", "🎯 互动练习",
         "🎮 选址仿真", "📝 知识测验", "📈 学习追踪", "ℹ️ 关于系统"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    # 快速进度条
    total_modules = 6
    done = sum(1 for m in st.session_state.learning_progress if st.session_state.learning_progress.get(m, 0) >= 60)
    st.caption(f"📊 学习进度：{done}/{total_modules} 模块")
    st.progress(done / total_modules if total_modules else 0)

    st.markdown("---")
    st.caption(f"系统版本：v2.0 | {datetime.now().strftime('%Y-%m-%d')}")

# ==================== 工具函数 ====================
def download_link(df, filename, text="下载数据"):
    """生成CSV下载链接"""
    csv = df.to_csv(index=False).encode('utf-8-sig')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def update_progress(module, score):
    if module not in st.session_state.learning_progress or st.session_state.learning_progress[module] < score:
        st.session_state.learning_progress[module] = score

def generate_demand_points(n, seed=None):
    """生成模拟需求点"""
    if seed is not None:
        np.random.seed(seed)
    return pd.DataFrame({
        '需求点': [f'客户{i+1}' for i in range(n)],
        'X坐标': np.random.randint(50, 450, n),
        'Y坐标': np.random.randint(50, 450, n),
        '年需求量': np.random.randint(50, 500, n),
        '运输费率': np.random.choice([0.8, 1.0, 1.2], n)
    })

# ==================== 首页 ====================
if page == "🏠 首页":
    st.markdown('<div class="main-header">🏭 仓库选址教学系统 v2.0</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🎓 欢迎来到深度优化的仓库选址教学系统！

    本系统面向物流管理、供应链专业学生，通过 **理论+计算+仿真+对比+测验**
    五位一体，帮助你从零到一掌握仓库选址的核心方法论。
    """)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📖 理论", "5章节", delta="核心知识")
    with col2:
        st.metric("🧮 计算", "6工具", delta="含迭代法")
    with col3:
        st.metric("📊 案例", "4企业", delta="深度分析")
    with col4:
        st.metric("🎯 练习", "20+题", delta="实战演练")
    with col5:
        st.metric("🎮 仿真", "3场景", delta="新增")

    st.markdown("---")

    st.markdown("### ✨ v2.0 新增特性")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🔬 科学计算增强**
        - 重心法**迭代收敛**过程可视化
        - **敏感度分析**：权重变化影响
        - **盈亏平衡分析**：成本拐点
        """)
    with col2:
        st.markdown("""
        **📊 决策工具扩展**
        - **多方案并行对比**面板
        - **蒙特卡洛仿真**：不确定性分析
        - **CSV数据导入/导出**
        """)
    with col3:
        st.markdown("""
        **🎓 学习体验优化**
        - **学习进度追踪**仪表盘
        - **题库扩充至20题**（随机抽题+限时）
        - **知识图谱**可视化
        """)

    st.markdown("---")
    st.markdown("### 📋 建议学习路径")
    path_steps = [
        ("1️⃣ 理论知识", "奠定基础 → 理解选址的本质和影响因素"),
        ("2️⃣ 计算工具", "动手实践 → 掌握重心法、加权评分、成本分析"),
        ("3️⃣ 敏感度分析", "深入思考 → 理解参数变化对决策的影响"),
        ("4️⃣ 案例分析", "学以致用 → 分析知名企业的真实选址策略"),
        ("5️⃣ 仿真练习", "综合训练 → 在模拟场景中做出选址决策"),
        ("6️⃣ 知识测验", "检验成果 → 评估知识掌握程度"),
    ]
    for step, desc in path_steps:
        st.markdown(f"**{step}** {desc}")

# ==================== 理论知识 ====================
elif page == "📖 理论知识":
    st.markdown('<div class="sub-header">📖 理论知识</div>', unsafe_allow_html=True)

    theory_tabs = st.tabs(["选址概述", "影响因素", "选址方法", "决策流程", "知识图谱"])

    with theory_tabs[0]:
        st.markdown("### 一、仓库选址概述")
        st.markdown("""
        #### 什么是仓库选址？
        仓库选址是在一定区域内，根据**物流需求、成本约束、服务要求**等因素，
        运用**科学方法**确定仓库最佳地理位置的过程。它是供应链管理中最具战略意义的决策之一。
        """)

        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **🏆 选址的战略意义：**
        - 📍 运输成本占物流总成本 **50%以上**，选址直接决定运输效率
        - ⏱️ 决定 **订单响应速度** 和服务水平（如"211限时达"依赖仓网布局）
        - 💼 关系企业 **竞争优势** —— 京东 vs 淘宝的核心差异之一
        - 🔄 **长期投资**，仓库一旦建成很难搬迁，决策影响10-20年
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### 选址的三层分类")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**🌐 战略型选址**\n\n服务于长期战略目标\n如：区域配送中心(RDC)\n影响周期：5-20年")
        with col2:
            st.success("**📦 战术型选址**\n\n满足中期运营需求\n如：季节仓、前置仓\n影响周期：1-5年")
        with col3:
            st.warning("**🚚 作业型选址**\n\n解决短期作业问题\n如：临时仓、中转仓\n影响周期：<1年")

        st.markdown("#### 选址 vs 选品：类比理解")
        st.markdown("""
        | 维度 | 仓库选址 | 零售店选址 |
        |------|---------|-----------|
        | 核心目标 | 最小化总物流成本 | 最大化客流/销售额 |
        | 关键指标 | 运输距离、仓储成本 | 人流量、商圈能级 |
        | 服务半径 | 50-500km | 1-5km |
        | 决策周期 | 10-20年 | 3-5年 |
        """)

    with theory_tabs[1]:
        st.markdown("### 二、选址影响因素")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🚚 运输因素")
            st.markdown("""
            - 交通便利性（公路、铁路、港口、机场）
            - 运输距离和成本
            - 运输方式的选择（整车 vs 零担）
            - 货物流向和流量
            - 返程空载率
            """)

            st.markdown("#### 💰 成本因素")
            st.markdown("""
            - 土地购置/租赁成本
            - 建设成本（仓库类型：普通/高标/冷链）
            - 运营成本（水电、维护、安保）
            - 运输成本（进货+出货）
            - 人力成本（当地工资水平）
            - 税收与补贴政策
            """)

        with col2:
            st.markdown("#### 🌍 环境因素")
            st.markdown("""
            - 自然条件（地形平坦度、气候、地质）
            - 基础设施（供水、供电、通信）
            - 城市规划与用地性质
            - 环保法规要求
            - 自然灾害风险评估
            """)

            st.markdown("#### 👥 市场因素")
            st.markdown("""
            - 客户地理分布与密度
            - 服务半径与时效要求
            - 市场需求预测（增长趋势）
            - 竞争对手仓库位置
            - 供应商分布
            """)

        st.markdown("---")
        st.markdown("#### 🔧 交互式因素重要性评估")

        factors = ['运输成本', '土地成本', '人力成本', '服务水平', '政策环境', '基础设施']
        weights = []
        cols = st.columns(len(factors))
        for i, factor in enumerate(factors):
            with cols[i]:
                w = st.slider(factor, 0, 100, [60, 40, 35, 50, 30, 30][i], key=f"theory_factor_{i}")
                weights.append(w)

        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'bar'}]],
                           subplot_titles=('因素权重分布', '因素重要性排序'))
        fig.add_trace(go.Pie(values=weights, labels=factors, hole=0.4), row=1, col=1)
        sorted_idx = np.argsort(weights)[::-1]
        fig.add_trace(go.Bar(x=[factors[i] for i in sorted_idx],
                            y=[weights[i] for i in sorted_idx],
                            marker_color=px.colors.qualitative.Plotly[:len(factors)]),
                     row=1, col=2)
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with theory_tabs[2]:
        st.markdown("### 三、选址方法详解")

        method_select = st.selectbox(
            "选择了解的方法",
            ["重心法", "迭代重心法（进阶）", "层次分析法（AHP）", "加权评分法",
             "线性规划法", "P-中值模型", "仿真模拟法"]
        )

        if method_select == "重心法":
            st.markdown("""
            #### 📍 重心法（Center of Gravity Method）

            **适用场景**：单一仓库选址，已知各需求点位置和需求量

            **核心思想**：找到使加权运输距离最小的位置

            **公式**：
            - X* = Σ(Vi × Xi × Ri) / Σ(Vi × Ri)
            - Y* = Σ(Vi × Yi × Ri) / Σ(Vi × Ri)

            其中 Vi=需求量, Xi/Yi=坐标, Ri=运输费率

            **关键假设**：运输成本与距离成正比（线性），且只考虑运输成本。
            """)

            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("""
            ✅ **优点**：计算直观、易于理解和实施
            ⚠️ **局限**：
            - 只考虑运输成本（忽略固定成本差异）
            - 假设运输成本与距离线性相关
            - 未考虑实际路网（使用直线距离）
            - 不适用于多仓库场景
            """)
            st.markdown('</div>', unsafe_allow_html=True)

        elif method_select == "迭代重心法（进阶）":
            st.markdown("""
            #### 🔄 迭代重心法（Iterative Center of Gravity）

            **与基本重心法的区别**：基本重心法假设运输成本与距离成**正比**，
            但实际中，运输成本往往与距离呈**非线性关系**（如阶梯定价）。
            迭代重心法通过多次迭代逐步逼近真实最优解。

            **迭代公式**：
            - X(k+1) = Σ(Vi × Xi × Ri / di(k)) / Σ(Vi × Ri / di(k))
            - Y(k+1) = Σ(Vi × Yi × Ri / di(k)) / Σ(Vi × Ri / di(k))
            - 其中 di(k) = √((Xi - Xk)² + (Yi - Yk)²)

            **收敛条件**：相邻两次迭代的坐标变化小于预设阈值（如 0.001）
            """)

            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("""
            💡 **教学要点**：迭代重心法展示了优化算法中"迭代收敛"的核心概念
            —— 从初始解出发，逐步改进直到稳定。这个过程与梯度下降、EM算法
            有相同的数学本质。
            """)
            st.markdown('</div>', unsafe_allow_html=True)

        elif method_select == "层次分析法（AHP）":
            st.markdown("""
            #### 🏗️ 层次分析法（AHP）

            **适用场景**：多准则决策，需综合定量与定性因素

            **四步法**：
            1. **建立层次结构**：目标层 → 准则层 → 方案层
            2. **构造判断矩阵**：两两比较相对重要性
            3. **层次单排序**：计算权重向量 + 一致性检验
            4. **层次总排序**：综合各层权重得出最终排序

            **1-9标度含义**：
            | 标度 | 含义 |
            |------|------|
            | 1 | 同等重要 |
            | 3 | 稍微重要 |
            | 5 | 明显重要 |
            | 7 | 强烈重要 |
            | 9 | 极端重要 |
            | 2,4,6,8 | 中间值 |

            **一致性检验**：CR = CI/RI < 0.10 表示判断矩阵一致性可接受
            """)

        elif method_select == "P-中值模型":
            st.markdown("""
            #### 📐 P-中值模型（P-Median Model）

            **适用场景**：从候选地址中选择P个仓库，使加权总距离最小

            **数学模型**（整数规划）：
            ```
            Min Σ Σ wi × dij × yij
            s.t.
              Σ xj = P              （恰好选择P个仓库）
              Σ yij = 1  ∀i         （每个客户只能由一个仓库服务）
              yij ≤ xj  ∀i,j        （只有开设的仓库才能服务）
              xj, yij ∈ {0, 1}      （二元决策变量）
            ```

            **商业应用**：联邦快递(FedEx)用P-中值模型优化全球转运中心布局
            """)

    with theory_tabs[3]:
        st.markdown("### 四、选址决策流程")

        # 决策流程图（用plotly画）
        stages = ['明确目标', '数据收集', '因素分析', '候选筛选', '方法计算', '评价比较', '最终决策', '实施监控']
        x_pos = list(range(len(stages)))
        y_pos = [0] * len(stages)

        fig = go.Figure()
        for i, (stage, x) in enumerate(zip(stages, x_pos)):
            color = ['#1565C0', '#1976D2', '#1E88E5', '#42A5F5', '#64B5F6', '#90CAF9', '#BBDEFB', '#E3F2FD'][i]
            fig.add_trace(go.Scatter(x=[x], y=[0], mode='markers+text',
                                     marker=dict(size=40, color=color, symbol='circle'),
                                     text=stage, textposition='middle center',
                                     textfont=dict(color='white' if i < 4 else '#333', size=10),
                                     name=stage, showlegend=False))
            if i < len(stages) - 1:
                fig.add_annotation(x=x+0.5, y=0, text="→",
                                   showarrow=False, font=dict(size=24, color='#1565C0'))

        fig.update_layout(title="选址决策流程", height=200,
                          xaxis=dict(range=[-0.5, len(stages)-0.5], showticklabels=False, showgrid=False),
                          yaxis=dict(range=[-1, 1], showticklabels=False, showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

        for i, (step, desc) in enumerate([
            ("1️⃣ 明确选址目标", "确定选址目的、服务范围、预算约束"),
            ("2️⃣ 收集相关数据", "客户分布、运输网络、土地价格、劳动力市场"),
            ("3️⃣ 分析影响因素", "确定各因素权重，评估影响程度"),
            ("4️⃣ 确定候选地址", "初步筛选3-5个备选地址"),
            ("5️⃣ 应用选址方法", "重心法定位 + 加权评分比较 + 成本分析"),
            ("6️⃣ 评价与比较", "综合考量定量与定性因素"),
            ("7️⃣ 确定最终选址", "做出决策，制定实施计划"),
        ]):
            st.markdown(f"**{step}**  {desc}")

    with theory_tabs[4]:
        st.markdown("### 五、知识图谱")

        st.markdown("#### 仓库选址知识体系")

        # 用雷达图展示不同方法的适用场景
        methods = ['重心法', '迭代重心法', 'AHP', '加权评分', '线性规划', '仿真模拟']
        dimensions = ['计算复杂度', '数据需求', '精确度', '多因素能力', '动态性']

        radar_data = {
            '重心法': [2, 3, 3, 1, 1],
            '迭代重心法': [4, 4, 4, 1, 2],
            'AHP': [5, 5, 4, 5, 2],
            '加权评分': [3, 4, 3, 4, 2],
            '线性规划': [5, 5, 5, 4, 3],
            '仿真模拟': [5, 5, 5, 5, 5],
        }

        method_choice = st.selectbox("选择方法查看能力画像", list(radar_data.keys()))

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=radar_data[method_choice],
            theta=dimensions,
            fill='toself',
            name=method_choice,
            line_color='#1565C0'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                          title=f"{method_choice} 能力画像", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        💡 **如何选择方法？**
        - **单一仓库 + 数据有限** → 重心法
        - **多因素综合决策** → AHP / 加权评分
        - **多仓库网络优化** → 线性规划 / P-中值
        - **高度不确定环境** → 蒙特卡洛仿真
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== 计算工具 ====================
elif page == "🧮 计算工具":
    st.markdown('<div class="sub-header">🧮 计算工具</div>', unsafe_allow_html=True)

    tool_tabs = st.tabs(["重心法（基础）", "迭代重心法（进阶）", "加权评分", "盈亏平衡分析", "成本估算器"])

    with tool_tabs[0]:
        st.markdown("### 📍 重心法计算器（基础版）")
        st.caption("使用加权平均法一次性计算最优仓库位置")

        col1, col2 = st.columns([3, 1])
        with col2:
            st.markdown("#### 数据导入")
            uploaded = st.file_uploader("上传CSV/Excel", type=['csv', 'xlsx'], key="cog_upload")
            if uploaded:
                try:
                    if uploaded.name.endswith('.csv'):
                        df = pd.read_csv(uploaded)
                    else:
                        df = pd.read_excel(uploaded)
                    st.success(f"已加载 {len(df)} 个需求点")
                except Exception as e:
                    st.error(f"读取失败：{e}")

            st.markdown("---")
            st.markdown("#### 快速生成")
            seed = st.number_input("随机种子", 0, 999, 42, key="cog_seed")
            if st.button("随机生成数据", key="cog_gen"):
                st.session_state['cog_data'] = generate_demand_points(
                    st.session_state.get('cog_n', 5), seed
                )

        with col1:
            st.markdown("#### 需求点数据")
            n = st.number_input("需求点数量", 2, 20, 5, key="cog_n")

            if 'cog_data' in st.session_state and st.session_state['cog_data'] is not None:
                default_data = st.session_state['cog_data']
            else:
                default_data = pd.DataFrame({
                    '需求点': [f'客户{i+1}' for i in range(n)],
                    'X坐标': [100 + i*60 for i in range(n)],
                    'Y坐标': [150 + i*40 for i in range(n)],
                    '年需求量': [100 + i*30 for i in range(n)],
                    '运输费率': [1.0] * n
                })

            edited = st.data_editor(default_data, num_rows="dynamic",
                                    use_container_width=True, key="cog_editor")

        if st.button("🚀 计算最优位置", type="primary", key="cog_calc"):
            try:
                x = edited['X坐标'].values
                y = edited['Y坐标'].values
                v = edited['年需求量'].values
                r = edited['运输费率'].values

                cnx = np.sum(v * r * x) / np.sum(v * r)
                cny = np.sum(v * r * y) / np.sum(v * r)

                # 计算各点距离和总成本
                distances = np.sqrt((x - cnx)**2 + (y - cny)**2)
                total_cost = np.sum(v * r * distances)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("最优 X 坐标", f"{cnx:.2f}")
                with col2:
                    st.metric("最优 Y 坐标", f"{cny:.2f}")
                with col3:
                    st.metric("总运输成本", f"{total_cost:.0f} 单位")

                # 可视化
                fig = go.Figure()
                for i in range(len(x)):
                    fig.add_trace(go.Scatter(
                        x=[x[i], cnx], y=[y[i], cny],
                        mode='lines', line=dict(color='lightgray', dash='dot'),
                        showlegend=False
                    ))

                fig.add_trace(go.Scatter(
                    x=x, y=y, mode='markers+text',
                    marker=dict(size=v/10, color='#42A5F5',
                               line=dict(color='#1565C0', width=1.5)),
                    text=edited['需求点'], textposition='top center',
                    name='需求点'
                ))
                fig.add_trace(go.Scatter(
                    x=[cnx], y=[cny], mode='markers+text',
                    marker=dict(size=22, color='#F44336', symbol='star',
                               line=dict(color='#B71C1C', width=2)),
                    text=['最优仓库'], textposition='bottom center',
                    name='最优位置'
                ))

                fig.update_layout(title="重心法选址结果", height=500,
                                  xaxis_title="X坐标", yaxis_title="Y坐标")

                st.plotly_chart(fig, use_container_width=True)

                # 导出
                result_df = pd.DataFrame({
                    '指标': ['最优X', '最优Y', '总运输成本', '最大距离', '平均距离'],
                    '值': [f"{cnx:.2f}", f"{cny:.2f}", f"{total_cost:.0f}",
                           f"{distances.max():.1f}", f"{distances.mean():.1f}"]
                })
                st.download_button("📥 下载结果CSV", result_df.to_csv(index=False).encode('utf-8-sig'),
                                   "重心法结果.csv", "text/csv")

                update_progress('重心法', 80)

            except Exception as e:
                st.error(f"计算错误：{e}")

    with tool_tabs[1]:
        st.markdown("### 🔄 迭代重心法（进阶版）")
        st.markdown("""
        > **核心思想**：基本重心法假设成本与距离成正比。但实际上成本函数可能是
        > 非线性的。迭代重心法通过反复优化，逐步逼近真实最优位置。
        """)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### 输入参数")
            n_iter = st.number_input("需求点数量", 2, 20, 5, key="iter_n")

            iter_data = pd.DataFrame({
                '需求点': [f'客户{i+1}' for i in range(n_iter)],
                'X坐标': [50 + np.random.randint(0, 400) for _ in range(n_iter)],
                'Y坐标': [50 + np.random.randint(0, 400) for _ in range(n_iter)],
                '年需求量': [100 + np.random.randint(0, 400) for _ in range(n_iter)],
                '运输费率': [1.0] * n_iter
            })
            iter_data = st.data_editor(iter_data, use_container_width=True, key="iter_editor")

        with col2:
            max_iterations = st.slider("最大迭代次数", 10, 200, 50, key="iter_max")
            tolerance = st.select_slider("收敛阈值", options=[0.1, 0.01, 0.001, 0.0001],
                                         value=0.01, key="iter_tol")
            st.markdown("---")
            st.markdown("**收敛条件**：")
            st.latex(r"\Delta = \sqrt{(X_{k+1}-X_k)^2 + (Y_{k+1}-Y_k)^2} < \epsilon")

        if st.button("🔄 开始迭代计算", type="primary", key="iter_calc"):
            x = iter_data['X坐标'].values
            y = iter_data['Y坐标'].values
            v = iter_data['年需求量'].values
            r = iter_data['运输费率'].values

            # 初始解：基本重心法
            xk = np.sum(v * r * x) / np.sum(v * r)
            yk = np.sum(v * r * y) / np.sum(v * r)

            history = [(xk, yk, 0)]
            converged = False
            final_iter = max_iterations

            for k in range(max_iterations):
                d = np.sqrt((x - xk)**2 + (y - yk)**2)
                d = np.maximum(d, 0.001)  # 防止除零

                w = v * r / d
                x_new = np.sum(w * x) / np.sum(w)
                y_new = np.sum(w * y) / np.sum(w)

                delta = np.sqrt((x_new - xk)**2 + (y_new - yk)**2)
                total_cost = np.sum(v * r * d)

                history.append((x_new, y_new, total_cost))
                xk, yk = x_new, y_new

                if delta < tolerance:
                    converged = True
                    final_iter = k + 1
                    break

            # 显示结果
            if converged:
                st.success(f"✅ 在第 {final_iter} 次迭代收敛！（阈值：{tolerance}）")
            else:
                st.warning(f"⚠️ 达到最大迭代次数 {max_iterations}，可能未完全收敛")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("收敛坐标 X", f"{xk:.3f}")
            with col2:
                st.metric("收敛坐标 Y", f"{yk:.3f}")
            with col3:
                st.metric("总迭代次数", f"{final_iter}")
            with col4:
                st.metric("总运输成本", f"{history[-1][2]:.0f}")

            # 迭代轨迹图
            hx = [h[0] for h in history]
            hy = [h[1] for h in history]

            fig = make_subplots(rows=1, cols=2, subplot_titles=('迭代轨迹','成本下降曲线'),
                               specs=[[{'type': 'scatter'}, {'type': 'scatter'}]])

            # 轨迹
            fig.add_trace(go.Scatter(x=hx, y=hy, mode='lines+markers',
                                     marker=dict(size=4, color='#1565C0'),
                                     line=dict(color='#1565C0', width=1.5),
                                     name='迭代路径'), row=1, col=1)
            fig.add_trace(go.Scatter(x=[hx[0]], y=[hy[0]], mode='markers',
                                     marker=dict(size=12, color='orange', symbol='circle'),
                                     name='初始位置'), row=1, col=1)
            fig.add_trace(go.Scatter(x=[hx[-1]], y=[hy[-1]], mode='markers',
                                     marker=dict(size=14, color='red', symbol='star'),
                                     name='最终位置'), row=1, col=1)
            fig.update_xaxes(title_text='X坐标', row=1, col=1)
            fig.update_yaxes(title_text='Y坐标', row=1, col=1)

            # 成本曲线
            costs = [h[2] for h in history if len(h) > 2 or h[2] > 0]
            # 需要重新计算每步成本
            step_costs = []
            for i, (hx_v, hy_v) in enumerate(zip(hx, hy)):
                d = np.sqrt((x - hx_v)**2 + (y - hy_v)**2)
                step_costs.append(np.sum(v * r * d))
            improvements = [step_costs[0] - c for c in step_costs]

            fig.add_trace(go.Scatter(x=list(range(len(step_costs))), y=step_costs,
                                     mode='lines+markers',
                                     marker=dict(size=4), name='总成本',
                                     line=dict(color='#E53935')), row=1, col=2)
            fig.update_xaxes(title_text='迭代次数', row=1, col=2)
            fig.update_yaxes(title_text='总运输成本', row=1, col=2)

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # 改进幅度
            improvement_pct = (step_costs[0] - step_costs[-1]) / step_costs[0] * 100
            st.info(f"📈 相比初始解，迭代法降低了 **{improvement_pct:.2f}%** 的运输成本")

            update_progress('迭代重心法', 90)

    with tool_tabs[2]:
        st.markdown("### 📊 加权评分计算器")
        st.markdown("对多个备选地址进行多因素综合评分")

        # 因素设置
        factors_input = st.text_area("评价因素（每行一个）",
                                     "运输便利性\n土地成本\n人力资源\n市场接近度\n政策环境\n基础设施",
                                     key="score_factors")
        factors = [f.strip() for f in factors_input.split('\n') if f.strip()]

        # 权重
        st.markdown("#### 设置权重")
        weights = {}
        cols = st.columns(len(factors))
        for i, f in enumerate(factors):
            with cols[i]:
                weights[f] = st.slider(f, 0, 100, 100 // len(factors), key=f"w_{f}")

        total_w = sum(weights.values())
        norm_w = {k: v/total_w for k, v in weights.items()} if total_w > 0 else {k: 0 for k in weights}

        # 备选地址评分
        st.markdown(f"#### 备选地址评分（权重总和={total_w}）")
        num_loc = st.number_input("备选地址数", 2, 8, 3, key="score_nl")

        st.caption(f"当前权重：{' | '.join(f'{k}={v/total_w*100:.0f}%' for k, v in weights.items())}")

        scores_data = {}
        for loc in range(num_loc):
            with st.expander(f"📍 地址 {loc+1}", expanded=(loc < 3)):
                cols = st.columns(len(factors))
                scores_data[f'地址{loc+1}'] = {}
                for i, f in enumerate(factors):
                    with cols[i]:
                        scores_data[f'地址{loc+1}'][f] = st.slider(
                            f"{f}", 0, 10, 5, key=f"loc{loc}_{f}_v2"
                        )

        if st.button("📊 计算综合得分", type="primary", key="score_calc"):
            results = []
            for loc_name, scores in scores_data.items():
                ws = sum(scores[f] * norm_w[f] for f in factors)
                results.append({
                    '地址': loc_name,
                    '加权得分(0-10)': round(ws, 2),
                    '百分制': round(ws * 10, 1),
                    **{f: scores[f] for f in factors}
                })

            results_df = pd.DataFrame(results).sort_values('加权得分(0-10)', ascending=False)

            st.success("✅ 评分完成！")
            st.dataframe(results_df.style.background_gradient(subset=['加权得分(0-10)'],
                                                              cmap='Blues'),
                        use_container_width=True)

            # 可视化
            fig = px.bar(results_df, x='地址', y='加权得分(0-10)',
                        title="各地址综合得分对比",
                        color='加权得分(0-10)', color_continuous_scale='Blues',
                        text=results_df['加权得分(0-10)'].apply(lambda x: f'{x:.2f}'))
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

            update_progress('加权评分', 80)

    with tool_tabs[3]:
        st.markdown("### ⚖️ 盈亏平衡分析")
        st.markdown("比较多个候选地址的固定成本与变动成本结构")

        num_bep = st.number_input("候选地址数", 2, 5, 2, key="bep_n")
        bep_data = []
        for i in range(num_bep):
            with st.expander(f"地址 {i+1} 成本参数"):
                col1, col2 = st.columns(2)
                with col1:
                    fixed = st.number_input(f"年固定成本（万元）", 0, 10000, [500, 300][i] if i < 2 else 400,
                                            key=f"bep_fixed_{i}")
                with col2:
                    var_unit = st.number_input(f"单位变动成本（元/吨）", 0.0, 1000.0,
                                               [20.0, 25.0][i] if i < 2 else 22.0, key=f"bep_var_{i}")
                bep_data.append({'地址': f'地址{i+1}', '固定成本(万元)': fixed, '变动成本(元/吨)': var_unit})

        max_vol = st.slider("最大年吞吐量（吨）", 1000, 500000, 200000, 10000, key="bep_vol")

        volumes = np.linspace(0, max_vol, 200)
        colors = ['#1565C0', '#E53935', '#2E7D32', '#F57C00', '#7B1FA2']

        fig = go.Figure()
        for i, bd in enumerate(bep_data):
            total = bd['固定成本(万元)'] * 10000 + volumes * bd['变动成本(元/吨)']
            fig.add_trace(go.Scatter(x=volumes, y=total / 10000,
                                     mode='lines', name=f"{bd['地址']}",
                                     line=dict(width=2.5, color=colors[i % len(colors)])))

        # 添加拐点标注
        if len(bep_data) >= 2:
            for i in range(len(bep_data)):
                for j in range(i+1, len(bep_data)):
                    f1, v1 = bep_data[i]['固定成本(万元)'] * 10000, bep_data[i]['变动成本(元/吨)']
                    f2, v2 = bep_data[j]['固定成本(万元)'] * 10000, bep_data[j]['变动成本(元/吨)']
                    if v1 != v2:
                        crossover = (f2 - f1) / (v1 - v2)
                        if 0 < crossover < max_vol:
                            fig.add_vline(x=crossover, line_dash="dash", line_color="gray", opacity=0.5)
                            y_cross = (f1 + v1 * crossover) / 10000
                            fig.add_annotation(x=crossover, y=y_cross,
                                               text=f"拐点:{crossover:.0f}吨",
                                               showarrow=True, arrowhead=2, ay=-30)

        fig.update_layout(title="盈亏平衡分析（总成本曲线）",
                          xaxis_title="年吞吐量（吨）", yaxis_title="总成本（万元）",
                          height=450)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        💡 **如何解读**：
        - 曲线交叉点 = 盈亏平衡量，低于此量选低固定成本地址，高于此量选低变动成本地址
        - 固定成本高的地址通常变动成本低（如自动化仓库）
        - 需要结合需求预测来做决策
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with tool_tabs[4]:
        st.markdown("### 💰 全面成本估算器")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 🏗️ 一次性投入")
            land = st.number_input("土地购置（万元）", 0, 10000, 500, key="ce_land")
            build = st.number_input("仓库建设（万元）", 0, 50000, 1000, key="ce_build")
            equip = st.number_input("设备采购（万元）", 0, 10000, 300, key="ce_equip")

        with col2:
            st.markdown("#### 🔧 年固定运营")
            labor = st.number_input("人力成本（万元/年）", 0, 5000, 200, key="ce_labor")
            util = st.number_input("水电能源（万元/年）", 0, 2000, 50, key="ce_util")
            maint = st.number_input("维修保养（万元/年）", 0, 1000, 30, key="ce_maint")
            mgmt = st.number_input("管理费（万元/年）", 0, 1000, 40, key="ce_mgmt")

        with col3:
            st.markdown("#### 🚚 运输成本")
            dist = st.number_input("平均运距（公里）", 0, 500, 80, key="ce_dist")
            rate = st.number_input("运输费率（元/吨·公里）", 0.0, 5.0, 0.5, step=0.1, key="ce_rate")
            volume = st.number_input("年吞吐量（吨）", 0, 1000000, 30000, key="ce_vol")

        years = st.slider("规划年限", 5, 30, 15, key="ce_years")

        fixed_total = land + build + equip
        annual_fixed = labor + util + maint + mgmt
        annual_transport = dist * rate * volume / 10000
        annual_total = annual_fixed + annual_transport
        lifecycle = fixed_total + annual_total * years

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("一次性投入", f"{fixed_total:.0f}万")
        with col2:
            st.metric("年运营成本", f"{annual_total:.0f}万")
        with col3:
            st.metric(f"{years}年总成本", f"{lifecycle:.0f}万")
        with col4:
            st.metric("吨均成本", f"{lifecycle*10000/(volume*years):.1f}元")

        # 成本结构饼图
        cost_items = ['土地', '建设', '设备', '人力', '水电', '维护', '管理', '运输']
        cost_vals = [land, build, equip, labor*years, util*years,
                     maint*years, mgmt*years, annual_transport*years]

        fig = px.pie(values=cost_vals, names=cost_items,
                    title=f"{years}年全生命周期成本结构", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

# ==================== 敏感度分析 ====================
elif page == "📊 敏感度分析":
    st.markdown('<div class="sub-header">📊 敏感度分析</div>', unsafe_allow_html=True)
    st.markdown("""
    敏感度分析帮助理解：**当某个参数变化时，选址决策如何变化？**
    这在不确定性高的环境中至关重要。
    """)

    analysis_type = st.selectbox("选择分析类型", [
        "权重敏感度（加权评分）",
        "需求敏感度（重心法）",
        "运输费率敏感度",
    ])

    if analysis_type == "权重敏感度（加权评分）":
        st.markdown("### 权重变化对评分的影响")

        st.markdown("#### 基准设置")
        factors_sa = ['运输便利', '土地成本', '人力成本', '市场接近']
        base_weights = {}
        cols = st.columns(len(factors_sa))
        for i, f in enumerate(factors_sa):
            with cols[i]:
                base_weights[f] = st.slider(f, 0, 100, 25, key=f"sa_base_{f}")

        total = sum(base_weights.values())
        base_norm = {k: v/total for k, v in base_weights.items()}

        st.markdown("#### 备选地址评分")
        loc_scores = {}
        for i in range(2):
            st.caption(f"**地址 {i+1}**")
            cols = st.columns(len(factors_sa))
            loc_scores[f'地址{i+1}'] = {}
            for j, f in enumerate(factors_sa):
                with cols[j]:
                    loc_scores[f'地址{i+1}'][f] = st.slider(
                        f"{f}", 0, 10, [7, 5][i] if j == 0 else [6, 8][i], key=f"sa_loc{i}_{f}"
                    )

        st.markdown("---")
        param_to_vary = st.selectbox("选择要变化的参数", factors_sa, key="sa_param")
        vary_range = st.slider(f"{param_to_vary} 权重变化范围", 0, 100, (10, 90), key="sa_range")

        if st.button("🔍 运行敏感度分析", type="primary", key="sa_run"):
            steps = 20
            weights_range = np.linspace(vary_range[0], vary_range[1], steps)
            scores_a, scores_b = [], []

            for w in weights_range:
                temp_w = base_weights.copy()
                temp_w[param_to_vary] = w
                tw_sum = sum(temp_w.values())
                temp_norm = {k: v/tw_sum for k, v in temp_w.items()}

                sa = sum(loc_scores['地址1'][f] * temp_norm[f] for f in factors_sa)
                sb = sum(loc_scores['地址2'][f] * temp_norm[f] for f in factors_sa)
                scores_a.append(sa)
                scores_b.append(sb)

            # 归一化权重显示
            norm_values = [w / (sum(base_weights.values()) - base_weights[param_to_vary] + w)
                           for w in weights_range]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=norm_values, y=scores_a,
                                     mode='lines', name='地址1',
                                     line=dict(width=2.5, color='#1565C0')))
            fig.add_trace(go.Scatter(x=norm_values, y=scores_b,
                                     mode='lines', name='地址2',
                                     line=dict(width=2.5, color='#E53935')))

            # 交叉点
            diffs = np.array(scores_a) - np.array(scores_b)
            sign_changes = np.where(np.diff(np.sign(diffs)))[0]
            for sc in sign_changes:
                fig.add_vline(x=norm_values[sc], line_dash="dash",
                             line_color="green", opacity=0.7)
                fig.add_annotation(x=norm_values[sc], y=(scores_a[sc] + scores_b[sc]) / 2,
                                  text="决策翻转点", showarrow=True, arrowhead=2)

            fig.update_layout(title=f'{param_to_vary} 权重敏感度分析',
                              xaxis_title=f'{param_to_vary} 归一化权重',
                              yaxis_title='综合评分', height=450)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown("""
            ⚠️ **解读要点**：
            - 如果曲线有交叉，说明存在**决策翻转点**——权重变化会导致推荐结果改变
            - 翻转点越靠近基准权重，决策越不稳定，需要更精确地确定权重
            - 如果两条曲线始终平行无交叉，说明该因素对方案排序影响不大
            """)
            st.markdown('</div>', unsafe_allow_html=True)

    elif analysis_type == "需求敏感度（重心法）":
        st.markdown("### 需求量变化对最优位置的影响")

        st.markdown("#### 输入需求点")
        n_sa = st.number_input("需求点数", 2, 10, 4, key="sa_demand_n")
        demand_data = pd.DataFrame({
            '需求点': [f'客户{i+1}' for i in range(n_sa)],
            'X': [100 + i*80 for i in range(n_sa)],
            'Y': [200 + (i%2)*150 for i in range(n_sa)],
            '需求': [100 + i*50 for i in range(n_sa)],
            '费率': [1.0] * n_sa
        })
        demand_data = st.data_editor(demand_data, use_container_width=True, key="sa_demand")

        vary_idx = st.selectbox("选择要变化需求量的需求点",
                                list(range(n_sa)), key="sa_vary_idx",
                                format_func=lambda x: f"客户{x+1}")
        vary_range_d = st.slider("需求量变化范围（倍数）", 0.1, 5.0, (0.5, 2.0), 0.1, key="sa_demand_range")

        if st.button("🔍 分析需求敏感度", type="primary", key="sa_demand_run"):
            xv = demand_data['X'].values.astype(float)
            yv = demand_data['Y'].values.astype(float)
            vv = demand_data['需求'].values.astype(float)
            rv = demand_data['费率'].values.astype(float)

            steps_d = 20
            multipliers = np.linspace(vary_range_d[0], vary_range_d[1], steps_d)
            cx_trace, cy_trace = [], []

            for mult in multipliers:
                v_temp = vv.copy()
                v_temp[vary_idx] = vv[vary_idx] * mult
                cx = np.sum(v_temp * rv * xv) / np.sum(v_temp * rv)
                cy = np.sum(v_temp * rv * yv) / np.sum(v_temp * rv)
                cx_trace.append(cx)
                cy_trace.append(cy)

            # 移动轨迹
            fig = make_subplots(rows=1, cols=2,
                               subplot_titles=('最优位置移动轨迹', '坐标随需求变化'))

            # 显示需求点
            fig.add_trace(go.Scatter(x=xv, y=yv, mode='markers+text',
                                     marker=dict(size=12, color='gray'),
                                     text=demand_data['需求点'],
                                     textposition='top center',
                                     name='需求点', showlegend=False), row=1, col=1)

            # 轨迹线
            fig.add_trace(go.Scatter(x=cx_trace, y=cy_trace, mode='lines+markers',
                                     marker=dict(size=5, color=cx_trace,
                                                colorscale='Viridis',
                                                showscale=True, colorbar=dict(title='倍率')),
                                     line=dict(width=2),
                                     name='最优位置轨迹'), row=1, col=1)

            fig.add_trace(go.Scatter(x=multipliers, y=cx_trace, mode='lines',
                                     name='X坐标', line=dict(color='#1565C0')),
                         row=1, col=2)
            fig.add_trace(go.Scatter(x=multipliers, y=cy_trace, mode='lines',
                                     name='Y坐标', line=dict(color='#E53935')),
                         row=1, col=2)

            fig.update_xaxes(title_text='X', row=1, col=1)
            fig.update_yaxes(title_text='Y', row=1, col=1)
            fig.update_xaxes(title_text='需求量倍数', row=1, col=2)
            fig.update_yaxes(title_text='坐标值', row=1, col=2)
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)

            motion_range = np.sqrt((max(cx_trace) - min(cx_trace))**2 +
                                   (max(cy_trace) - min(cy_trace))**2)
            st.info(f"📐 最优位置移动范围：**{motion_range:.1f}** 单位（表示需求不确定性对决策的影响程度）")

# ==================== 多方案对比 ====================
elif page == "📋 多方案对比":
    st.markdown('<div class="sub-header">📋 多方案并行对比</div>', unsafe_allow_html=True)
    st.markdown("输入多个候选方案，进行多维度并行对比分析")

    num_compare = st.slider("候选方案数", 2, 5, 3, key="cmp_n")

    criteria = ['土地成本', '交通便利', '劳动力', '市场接近', '政策环境',
                '基础设施', '扩展空间', '环境风险']
    criteria_input = st.text_area("评价维度（可修改）", '\n'.join(criteria), key="cmp_criteria")
    criteria_list = [c.strip() for c in criteria_input.split('\n') if c.strip()]

    st.markdown("#### 各方案评分（1-10）")
    cmp_scores = {}
    for i in range(num_compare):
        with st.expander(f"方案 {chr(65+i)}", expanded=(i < 3)):
            cols = st.columns(len(criteria_list))
            cmp_scores[f'方案{chr(65+i)}'] = {}
            for j, c in enumerate(criteria_list):
                with cols[j]:
                    cmp_scores[f'方案{chr(65+i)}'][c] = st.slider(
                        c, 0, 10, 5, key=f"cmp_{i}_{j}"
                    )

    if st.button("📊 生成对比报告", type="primary", key="cmp_run"):
        cmp_df = pd.DataFrame(cmp_scores).T
        cmp_df.index.name = '方案'

        # 雷达图
        fig = go.Figure()
        colors_cmp = ['#1565C0', '#E53935', '#2E7D32', '#F57C00', '#7B1FA2']
        for i, (scheme, row) in enumerate(cmp_df.iterrows()):
            fig.add_trace(go.Scatterpolar(
                r=row.values, theta=criteria_list, fill='toself',
                name=scheme, line=dict(color=colors_cmp[i % len(colors_cmp)]),
                opacity=0.6
            ))

        fig.update_layout(title="多方案雷达对比", polar=dict(radialaxis=dict(range=[0, 10])),
                          height=500)
        st.plotly_chart(fig, use_container_width=True)

        # 热力图
        fig2 = px.imshow(cmp_df.T, text_auto=True, aspect="auto",
                        color_continuous_scale='Blues',
                        title="方案评分热力图")
        st.plotly_chart(fig2, use_container_width=True)

        # 总分对比
        cmp_df['总分'] = cmp_df.sum(axis=1)
        cmp_df['平均分'] = cmp_df['总分'] / len(criteria_list)
        fig3 = px.bar(cmp_df.reset_index(), x='方案', y='平均分',
                     color='平均分', text=cmp_df['平均分'].round(1),
                     color_continuous_scale='Blues', title="综合评分对比")
        fig3.update_traces(textposition='outside')
        st.plotly_chart(fig3, use_container_width=True)

        st.download_button("📥 导出对比报告", cmp_df.to_csv().encode('utf-8-sig'),
                          "方案对比报告.csv", "text/csv")

# ==================== 案例分析 ====================
elif page == "📊 案例分析":
    st.markdown('<div class="sub-header">📊 案例分析</div>', unsafe_allow_html=True)

    case_tabs = st.tabs(["京东物流", "亚马逊FBA", "菜鸟网络", "某制造企业"])

    with case_tabs[0]:
        st.markdown("### 京东物流仓网布局")

        st.markdown("""
        #### 🏢 企业背景
        京东物流是中国最大的一体化供应链物流服务商，其仓储网络是其**核心竞争力**。
        截至2024年，全国拥有**1600+**仓库，总面积超**3200万平方米**。

        #### 📍 仓网层级结构
        """)

        # 层级可视化
        levels = ['亚洲一号\n(全国枢纽)', '区域RDC\n(省际分拨)', '城市FDC\n(同城配送)',
                  '前置仓\n(3km覆盖)', '服务站\n(末端触达)']
        sizes = [40, 200, 500, 600, 200]
        radii = ['500km', '200km', '50km', '10km', '3km']

        fig = go.Figure()
        for i, (level, size, radius) in enumerate(zip(levels, sizes, radii)):
            y = 4 - i
            fig.add_trace(go.Scatter(
                x=[size/2], y=[y], mode='markers+text',
                marker=dict(size=size/10, color=['#B71C1C', '#E53935', '#F57C00',
                                                  '#FFA726', '#FFCC80'][i]),
                text=f'{level}<br>{radius}', textposition='middle right',
                name=level, showlegend=False
            ))

        fig.update_layout(title="京东仓网层级结构（气泡大小=数量）",
                          height=400, showlegend=False,
                          xaxis=dict(showticklabels=False, showgrid=False),
                          yaxis=dict(showticklabels=False, showgrid=False, range=[-0.5, 4.5]))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("""
        **📚 教学启示：**
        1. **分层选址**：不同层级仓库有不同服务半径和功能定位
        2. **以客户为中心**：前置仓策略确保"211"限时达体验
        3. **规模效应**：仓网密度越高，边际配送成本越低
        4. **动态调整**：根据订单密度数据动态优化仓网布局
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with case_tabs[1]:
        st.markdown("### 亚马逊FBA全球选址")
        st.markdown("""
        #### 背景
        FBA (Fulfillment by Amazon) 全球**400+**运营中心，
        其中北美约**150个**，欧洲约**70个**。

        #### 选址关键指标体系
        """)

        factors_df = pd.DataFrame({
            '因素': ['人口密度', '交通网络', '劳动力', '土地成本', '税收优惠', '气候条件'],
            '权重(%)': [25, 25, 20, 15, 10, 5],
            '量化指标': ['50km内人口>100万', '3条以上州际公路', '失业率4-8%',
                       '均价低于区域均值', '州税减免政策', '自然灾害风险低']
        })
        st.dataframe(factors_df, use_container_width=True)

        st.info("""
        **亚马逊的选址创新**：
        - 🧠 **机器学习预测**：基于历史订单预测各区域未来需求
        - 🗺️ **GIS地理信息系统**：叠加人口密度、交通网络、劳动力市场等图层
        - 📐 **多目标优化**：同时优化配送时效（Prime 2日达）、成本和碳排放
        """)

    with case_tabs[2]:
        st.markdown("### 菜鸟网络智能选址")
        st.markdown("""
        #### 🧠 AI驱动的选址决策

        菜鸟网络作为阿里巴巴的物流数据平台，不直接拥有仓库，而是
        通过**大数据和AI算法**帮助合作伙伴优化仓网布局。

        #### 智能选址架构
        """)

        # 架构图
        arch_data = pd.DataFrame({
            '层级': ['数据层', '算法层', '决策层', '执行层'],
            '内容': [
                '订单热力图、消费者画像、LBS数据',
                '需求预测模型、选址优化模型、仿真验证',
                '多方案生成、风险评估、ROI分析',
                '自动化仓搭建、动态库存调配'
            ],
            '技术': ['Hadoop/Spark', '运筹优化+ML', '可视化BI', 'IoT+AGV']
        })
        st.dataframe(arch_data, use_container_width=True)

        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **技术亮点**：
        - 📊 **数据驱动**：分析数亿订单的城市级分布
        - 🤖 **AI预测**：提前3-6个月预测区域需求增长
        - 🔄 **动态优化**：季节性需求波动自动调整仓容
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with case_tabs[3]:
        st.markdown("### 某制造企业华东RDC选址")
        st.markdown("#### 📋 项目背景")
        st.markdown("年处理量1400万件，服务江浙沪皖四地客户")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**客户分布**")
            customer_df = pd.DataFrame({
                '区域': ['江苏', '浙江', '上海', '安徽'],
                '客户数': [120, 80, 60, 40],
                '年需求(万件)': [500, 400, 300, 200],
                '坐标X': [250, 200, 280, 180],
                '坐标Y': [280, 220, 260, 240]
            })
            st.dataframe(customer_df, use_container_width=True)

        with col2:
            st.markdown("**候选城市**")
            cities_df = pd.DataFrame({
                '城市': ['苏州', '杭州', '南京', '合肥'],
                '土地成本(万/亩)': [80, 120, 70, 45],
                '交通指数(百)': [95, 90, 85, 80],
                '市场接近度': [90, 95, 75, 70],
                '人力成本指数': [85, 95, 75, 60]
            })
            st.dataframe(cities_df, use_container_width=True)

        if st.button("▶️ 演示决策过程", key="case_demo"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Step 1/4: 重心法初步定位...")
            time.sleep(0.3)
            progress_bar.progress(25)

            xv = customer_df['坐标X'].values
            yv = customer_df['坐标Y'].values
            vv = customer_df['年需求(万件)'].values
            cx = np.sum(vv * xv) / np.sum(vv)
            cy = np.sum(vv * yv) / np.sum(vv)
            st.info(f"初步最优坐标：X={cx:.1f}, Y={cy:.1f}（靠近江浙沪交界）")

            status_text.text("Step 2/4: 加权评分...")
            time.sleep(0.3)
            progress_bar.progress(50)
            st.dataframe(pd.DataFrame({
                '城市': ['苏州', '杭州', '南京', '合肥'],
                '综合得分': [87, 82, 78, 72],
                '排名': [1, 2, 3, 4]
            }), use_container_width=True)

            status_text.text("Step 3/4: 盈亏平衡分析...")
            time.sleep(0.3)
            progress_bar.progress(75)
            st.info("苏州 vs 合肥：拐点约8万件/年，当前需求1400万件远超拐点，选择苏州")

            status_text.text("Step 4/4: 最终决策...")
            time.sleep(0.3)
            progress_bar.progress(100)

            st.success("""
            ### ✅ 最终推荐：苏州市

            **决策依据：**
            1. 📍 重心法显示最优位置靠近苏州方向
            2. 📊 加权评分87分，排名第1
            3. ⚖️ 超越盈亏平衡点，适合大规模运营
            4. 🚚 交通枢纽，辐射江浙沪
            5. 🏭 物流园区配套完善
            """)

            status_text.empty()

# ==================== 互动练习 ====================
elif page == "🎯 互动练习":
    st.markdown('<div class="sub-header">🎯 互动练习</div>', unsafe_allow_html=True)

    ex_tabs = st.tabs(["选址模拟器", "场景决策", "计算练习"])

    with ex_tabs[0]:
        st.markdown("### 🕹️ 选址模拟器")
        st.markdown("拖动滑竿选择仓库位置，观察成本和服务覆盖的变化")

        col1, col2 = st.columns([3, 1])
        with col2:
            n_ex = st.slider("需求点数量", 5, 25, 10, key="ex_n")
            if st.button("🔄 重新生成", key="ex_regenerate"):
                st.session_state['ex_points'] = generate_demand_points(n_ex, random.randint(0, 9999))

        with col1:
            if 'ex_points' not in st.session_state or st.session_state['ex_points'] is None:
                st.session_state['ex_points'] = generate_demand_points(n_ex, 42)

            points = st.session_state['ex_points']

            wh_x = st.slider("仓库 X 坐标", 0, 500, 250, key="ex_whx")
            wh_y = st.slider("仓库 Y 坐标", 0, 500, 250, key="ex_why")

            # 计算
            points['距离'] = np.sqrt((points['X坐标'] - wh_x)**2 + (points['Y坐标'] - wh_y)**2)
            points['运输成本'] = points['距离'] * points['年需求量'] * points['运输费率'] * 0.01
            total_cost = points['运输成本'].sum()

            # 展示地图
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=points['X坐标'], y=points['Y坐标'],
                mode='markers+text',
                marker=dict(size=points['年需求量']/8, color='#42A5F5',
                           line=dict(color='#1565C0', width=1)),
                text=points['需求点'], textposition='top center',
                name='客户'
            ))
            fig.add_trace(go.Scatter(
                x=[wh_x], y=[wh_y], mode='markers',
                marker=dict(size=22, color='red', symbol='star',
                           line=dict(color='darkred', width=2)),
                name='仓库'
            ))
            # 服务范围
            for radius in [80, 150]:
                theta = np.linspace(0, 2*np.pi, 100)
                fig.add_trace(go.Scatter(
                    x=wh_x + radius * np.cos(theta),
                    y=wh_y + radius * np.sin(theta),
                    mode='lines', line=dict(dash='dash', color='green' if radius == 80 else 'orange',
                                           width=1),
                    name=f'{radius}km 覆盖圈', showlegend=True
                ))

            fig.update_layout(title="选址模拟地图", height=500,
                             xaxis_title="X坐标", yaxis_title="Y坐标")
            st.plotly_chart(fig, use_container_width=True)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总运输成本", f"{total_cost:.0f}万元")
            with col2:
                st.metric("平均距离", f"{points['距离'].mean():.0f}km")
            with col3:
                st.metric("最大距离", f"{points['距离'].max():.0f}km")
            with col4:
                st.metric("覆盖客户", f"{(points['距离'] <= 80).sum()}/{len(points)}")

            # 对比最优解
            cx_opt = np.sum(points['年需求量'] * points['运输费率'] * points['X坐标']) / \
                     np.sum(points['年需求量'] * points['运输费率'])
            cy_opt = np.sum(points['年需求量'] * points['运输费率'] * points['Y坐标']) / \
                     np.sum(points['年需求量'] * points['运输费率'])
            opt_distances = np.sqrt((points['X坐标'] - cx_opt)**2 + (points['Y坐标'] - cy_opt)**2)
            opt_cost = np.sum(points['年需求量'] * points['运输费率'] * opt_distances * 0.01)

            if total_cost > opt_cost * 1.05:
                st.warning(f"💡 当前成本比理论最优高 **{(total_cost/opt_cost - 1)*100:.1f}%**，试试 (X={cx_opt:.0f}, Y={cy_opt:.0f})")

    with ex_tabs[1]:
        st.markdown("### 🎯 场景决策练习")

        scenario = st.selectbox("选择场景", [
            "电商华南RDC选址",
            "冷链中心选址",
            "跨境仓选址",
        ])

        if scenario == "电商华南RDC选址":
            st.markdown("""
            #### 场景：电商企业华南区域配送中心选址

            年订单量 **100万单**，服务广东、广西、福建三省。
            """)

            cities = pd.DataFrame({
                '城市': ['广州', '深圳', '东莞', '佛山'],
                '土地成本': [80, 120, 50, 60],
                '人力成本': [8, 10, 6, 7],
                '交通指数': [95, 90, 85, 80],
                '市场接近度': [90, 95, 75, 70],
            })
            st.dataframe(cities, use_container_width=True)

            choice = st.selectbox("选择你的推荐城市", cities['城市'], key="sc_city")
            reason = st.text_area("说明理由", placeholder="考虑成本、交通、市场等因素...", key="sc_reason")

            if st.button("提交决策", key="sc_submit"):
                feedback = {
                    '广州': "✅ 综合最优：交通枢纽+市场辐射，适合追求服务品质",
                    '深圳': "⚠️ 成本最高但市场活跃，适合高端跨境电商",
                    '东莞': "💰 性价比之选：成本低但市场辐射弱",
                    '佛山': "📊 稳健选择：各项指标均衡"
                }
                st.info(feedback[choice])
                if reason:
                    st.success("✅ 决策已记录。良好的决策需要数据支撑+经验判断！")

    with ex_tabs[2]:
        st.markdown("### 📝 计算练习")

        ex_type = st.selectbox("练习类型", ["重心法", "加权评分", "盈亏分析"])

        if ex_type == "重心法":
            st.markdown("""
            #### 练习题
            | 城市 | X | Y | 年需求量(吨) |
            |---|---|---|---|
            | A市 | 100 | 200 | 500 |
            | B市 | 300 | 100 | 300 |
            | C市 | 200 | 300 | 400 |
            """)

            user_x = st.number_input("你的X坐标", 0, 500, key="gex_x")
            user_y = st.number_input("你的Y坐标", 0, 500, key="gex_y")

            if st.button("检查答案", key="gex_check"):
                cx = (100*500 + 300*300 + 200*400) / 1200
                cy = (200*500 + 100*300 + 300*400) / 1200
                err = np.sqrt((user_x - cx)**2 + (user_y - cy)**2)

                st.markdown(f"**正确答案**：X={cx:.2f}, Y={cy:.2f}")

                if err < 3:
                    st.success(f"🎉 完美！误差仅 {err:.2f}")
                elif err < 15:
                    st.warning(f"接近正确，误差 {err:.1f}")
                else:
                    st.error(f"需要重新计算，误差 {err:.1f}")

        elif ex_type == "盈亏分析":
            st.markdown("""
            #### 练习题
            仓库A：年固定成本300万，变动成本15元/吨
            仓库B：年固定成本500万，变动成本10元/吨

            求盈亏平衡点的年吞吐量。
            """)

            user_bep = st.number_input("盈亏平衡量（吨）", 0, 500000, key="bep_ex")

            if st.button("检查答案", key="bep_check"):
                correct_bep = (500 - 300) * 10000 / (15 - 10)
                st.markdown(f"**正确答案**：{correct_bep:.0f} 吨")

                if abs(user_bep - correct_bep) / correct_bep < 0.05:
                    st.success("✅ 正确！")
                else:
                    st.error(f"计算有误。公式：(500-300)×10000 / (15-10) = {correct_bep:.0f}")

# ==================== 选址仿真 ====================
elif page == "🎮 选址仿真":
    st.markdown('<div class="sub-header">🎮 选址仿真实验</div>', unsafe_allow_html=True)
    st.markdown("通过蒙特卡洛仿真，探索不确定性下的选址决策")

    sim_type = st.selectbox("仿真类型", [
        "需求不确定性仿真",
        "多场景蒙特卡洛",
    ])

    if sim_type == "需求不确定性仿真":
        st.markdown("### 需求波动下的最优位置稳定性")

        n_sim = st.slider("需求点数量", 3, 8, 5, key="sim_n")
        n_runs = st.slider("仿真次数", 100, 2000, 500, 100, key="sim_runs")
        uncertainty = st.slider("需求波动幅度(%)", 5, 50, 20, key="sim_unc")

        st.markdown("#### 需求点基础数据")
        sim_data = pd.DataFrame({
            '需求点': [f'P{i+1}' for i in range(n_sim)],
            'X': np.random.randint(50, 450, n_sim),
            'Y': np.random.randint(50, 450, n_sim),
            '基础需求量': np.random.randint(100, 500, n_sim),
        })
        sim_data = st.data_editor(sim_data, use_container_width=True, key="sim_data")

        if st.button("🚀 运行仿真", type="primary", key="sim_run"):
            xv = sim_data['X'].values
            yv = sim_data['Y'].values
            bv = sim_data['基础需求量'].values

            cx_results, cy_results = [], []
            progress_bar = st.progress(0)

            np.random.seed(42)
            for i in range(n_runs):
                noise = 1 + np.random.uniform(-uncertainty/100, uncertainty/100, len(bv))
                dv = bv * noise
                cx_results.append(np.sum(dv * xv) / np.sum(dv))
                cy_results.append(np.sum(dv * yv) / np.sum(dv))
                if i % (n_runs // 10) == 0:
                    progress_bar.progress(i / n_runs)

            progress_bar.progress(1.0)

            # 可视化分布
            fig = make_subplots(rows=1, cols=2, subplot_titles=('最优位置分布热力图', '坐标值波动'))

            fig.add_trace(go.Histogram2d(x=cx_results, y=cy_results,
                                         colorscale='Blues', nbinsx=30, nbinsy=30,
                                         name='密度'), row=1, col=1)
            fig.add_trace(go.Scatter(x=xv, y=yv, mode='markers+text',
                                     marker=dict(size=10, color='red'),
                                     text=sim_data['需求点'],
                                     textposition='top center',
                                     name='需求点', showlegend=False), row=1, col=1)

            fig.add_trace(go.Scatter(y=cx_results, mode='lines',
                                     name='X坐标', line=dict(color='#1565C0')),
                         row=1, col=2)
            fig.add_trace(go.Scatter(y=cy_results, mode='lines',
                                     name='Y坐标', line=dict(color='#E53935')),
                         row=1, col=2)

            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)

            # 统计
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("X 均值±σ", f"{np.mean(cx_results):.1f}±{np.std(cx_results):.1f}")
            with col2:
                st.metric("Y 均值±σ", f"{np.mean(cy_results):.1f}±{np.std(cy_results):.1f}")
            with col3:
                st.metric("95%置信椭圆面积",
                         f"{np.pi * 2.45 * np.std(cx_results) * np.std(cy_results):.0f}")

            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(f"""
            💡 **仿真结论**：
            - 需求波动 **{uncertainty}%** 时，最优位置在 X:[{np.mean(cx_results)-2*np.std(cx_results):.0f}, {np.mean(cx_results)+2*np.std(cx_results):.0f}],
              Y:[{np.mean(cy_results)-2*np.std(cy_results):.0f}, {np.mean(cy_results)+2*np.std(cy_results):.0f}] 范围内
            - 波动越大，最优位置的**不确定性区域**越大
            - 实际决策中可在此区域内结合其他因素（土地价格等）最终确定
            """)
            st.markdown('</div>', unsafe_allow_html=True)

    elif sim_type == "多场景蒙特卡洛":
        st.markdown("### 多场景随机仿真对比")
        st.markdown("比较多个候选地址在不同需求场景下的表现")

        st.markdown("#### 定义场景")
        num_scenarios = st.slider("场景数量", 2, 4, 3, key="mc_ns")
        scenarios = {}
        for i in range(num_scenarios):
            with st.expander(f"场景 {i+1}"):
                col1, col2 = st.columns(2)
                with col1:
                    s_name = st.text_input("场景名称", f"场景{i+1}", key=f"mc_name_{i}")
                    s_prob = st.slider("发生概率(%)", 0, 100, 100//num_scenarios, key=f"mc_prob_{i}")
                with col2:
                    s_demand = st.number_input("总需求(吨)", 1000, 100000, 20000, 5000, key=f"mc_demand_{i}")
                    s_rate = st.number_input("费率(元/吨公里)", 0.1, 2.0, 0.5, 0.1, key=f"mc_rate_{i}")
                scenarios[s_name] = {'概率': s_prob, '需求': s_demand, '费率': s_rate}

        st.markdown("#### 候选地址参数")
        num_candidates = st.slider("候选地址数", 2, 4, 2, key="mc_nc")
        candidates = {}
        for i in range(num_candidates):
            with st.expander(f"地址 {i+1}"):
                col1, col2 = st.columns(2)
                with col1:
                    c_name = st.text_input("地址名称", f"地址{i+1}", key=f"mc_cname_{i}")
                    c_fixed = st.number_input("年固定成本(万)", 0, 5000, 300, 100, key=f"mc_fixed_{i}")
                with col2:
                    c_var = st.number_input("变动成本(元/吨)", 0.0, 100.0, 20.0, key=f"mc_var_{i}")
                    c_dist = st.number_input("平均运距(km)", 10, 500, 100, key=f"mc_dist_{i}")
                candidates[c_name] = {'固定成本': c_fixed, '变动成本': c_var, '运距': c_dist}

        if st.button("🎲 运行蒙特卡洛", type="primary", key="mc_run"):
            mc_runs = st.slider("仿真次数", 500, 5000, 1000, 500, key="mc_runs_slider")

            # 构建概率分布
            s_names = list(scenarios.keys())
            s_probs = np.array([scenarios[s]['概率'] for s in s_names])
            s_probs = s_probs / s_probs.sum()

            np.random.seed(42)
            winner_count = {c: 0 for c in candidates}

            for _ in range(mc_runs):
                s = np.random.choice(s_names, p=s_probs)
                sc = scenarios[s]

                best = None
                best_cost = float('inf')
                for cn, cp in candidates.items():
                    cost = cp['固定成本'] * 10000 + cp['变动成本'] * sc['需求'] + \
                           cp['运距'] * sc['费率'] * sc['需求']
                    if cost < best_cost:
                        best_cost = cost
                        best = cn
                winner_count[best] += 1

            # 结果
            winner_df = pd.DataFrame({
                '地址': list(winner_count.keys()),
                '胜出次数': list(winner_count.values()),
                '胜率(%)': [v/mc_runs*100 for v in winner_count.values()]
            }).sort_values('胜率(%)', ascending=False)

            fig = px.bar(winner_df, x='地址', y='胜率(%)',
                        title=f"蒙特卡洛仿真结果（{mc_runs}次）",
                        color='胜率(%)', text=winner_df['胜率(%)'].round(1),
                        color_continuous_scale='Blues')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(winner_df, use_container_width=True)

# ==================== 知识测验 ====================
elif page == "📝 知识测验":
    st.markdown('<div class="sub-header">📝 知识测验</div>', unsafe_allow_html=True)

    # 扩充题库
    question_bank = [
        # 基础题 (level 1)
        {"question": "运输成本通常占物流总成本的：", "options": ["20-30%", "30-40%", "50%以上", "10-20%"],
         "answer": 2, "level": 1, "explanation": "运输成本是物流最大成本项，占比超50%。", "topic": "基础概念"},
        {"question": "重心法最适合的场景是：", "options": ["多仓库选址", "单一仓库选址", "冷链仓库", "跨境仓库"],
         "answer": 1, "level": 1, "explanation": "重心法适用于单一仓库选址。", "topic": "方法选择"},
        {"question": "以下哪项不是选址的主要因素？", "options": ["交通便利", "土地成本", "品牌形象", "人力资源"],
         "answer": 2, "level": 1, "explanation": "品牌形象不是选址的直接因素。", "topic": "影响因素"},
        {"question": "仓库选址属于哪种决策类型？", "options": ["日常运营", "战术决策", "战略决策", "紧急决策"],
         "answer": 2, "level": 1, "explanation": "选址影响10-20年，属于战略决策。", "topic": "基础概念"},
        {"question": "京东物流的核心选址策略是：", "options": ["成本最低", "贴近消费者", "土地最便宜", "政策最优"],
         "answer": 1, "level": 1, "explanation": "京东以贴近消费者为核心策略。", "topic": "案例分析"},

        # 进阶题 (level 2)
        {"question": "AHP判断矩阵中'5'表示：", "options": ["同等重要", "稍微重要", "明显重要", "强烈重要"],
         "answer": 2, "level": 2, "explanation": "1同等/3稍微/5明显/7强烈/9极端。", "topic": "方法细节"},
        {"question": "迭代重心法相比基本重心法的优势是：", "options": ["计算更快", "考虑非线性成本", "不需要数据", "支持多仓库"],
         "answer": 1, "level": 2, "explanation": "迭代法可处理非线性距离成本函数。", "topic": "方法对比"},
        {"question": "P-中值模型求解的是：", "options": ["单仓库最优位置", "P个仓库最优位置", "仓库最优容量", "最优库存水平"],
         "answer": 1, "level": 2, "explanation": "P-中值模型选择P个仓库使总距离最小。", "topic": "方法细节"},
        {"question": "盈亏平衡分析的目的是：", "options": ["计算总投资", "比较固定与变动成本结构", "预测需求", "评估风险"],
         "answer": 1, "level": 2, "explanation": "分析不同成本结构方案的适用量区间。", "topic": "成本分析"},
        {"question": "敏感度分析主要回答什么问题？", "options": ["选址在哪里", "结果对参数变化的敏感程度", "需要多少钱", "何时建仓"],
         "answer": 1, "level": 2, "explanation": "敏感度分析评估参数不确定性对决策的影响。", "topic": "分析方法"},

        # 挑战题 (level 3)
        {"question": "蒙特卡洛仿真在选址中的作用是：", "options": ["精确计算位置", "评估不确定性下的决策稳健性", "取代其他方法", "验证数据准确性"],
         "answer": 1, "level": 3, "explanation": "通过大量随机模拟评估决策在不同场景下的表现。", "topic": "高级方法"},
        {"question": "在AHP中，CR>0.10表示：", "options": ["模型最优", "一致性可接受", "需要修正判断矩阵", "计算完成"],
         "answer": 2, "level": 3, "explanation": "一致性比率>0.10表示判断矩阵不一致，需调整。", "topic": "方法细节"},
        {"question": "仓库选址中'牛鞭效应'会影响：", "options": ["运输成本", "需求预测准确性", "土地价格", "员工招聘"],
         "answer": 1, "level": 3, "explanation": "牛鞭效应导致需求信息扭曲，影响选址基础数据。", "topic": "供应链"},
        {"question": "服务水平约束下的选址模型中，约束通常表达为：", "options": ["成本<预算", "距离<最大服务距离", "仓库>最小容量", "员工>最小人数"],
         "answer": 1, "level": 3, "explanation": "服务约束通常以最大配送距离/时间表达。", "topic": "高级方法"},
        {"question": "多目标选址优化中常见的两个冲突目标是：", "options": ["面积和高度", "成本和成本", "成本和服务水平", "温度和湿度"],
         "answer": 2, "level": 3, "explanation": "降低成本和提升服务通常是矛盾的目标。", "topic": "高级方法"},
    ]

    # 测验设置
    st.markdown("### ⚙️ 测验设置")
    col1, col2, col3 = st.columns(3)
    with col1:
        quiz_mode = st.radio("测验模式", ["标准模式", "限时挑战", "主题专练"], key="quiz_mode")
    with col2:
        n_questions = st.slider("题目数量", 5, 15, 10, key="quiz_nq")
    with col3:
        difficulty = st.selectbox("难度", ["全部", "基础(Level 1)", "进阶(Level 2)", "挑战(Level 3)"], key="quiz_diff")

    # 初始化
    if 'quiz_initialized' not in st.session_state or st.session_state.get('quiz_mode_prev') != quiz_mode:
        st.session_state.quiz_initialized = True
        st.session_state.quiz_mode_prev = quiz_mode
        st.session_state.quiz_submitted = False
        st.session_state.quiz_start_time = time.time()

        # 选题
        available = question_bank.copy()
        if difficulty != "全部":
            level_map = {"基础(Level 1)": 1, "进阶(Level 2)": 2, "挑战(Level 3)": 3}
            available = [q for q in available if q['level'] == level_map[difficulty]]

        if quiz_mode == "主题专练":
            topics = list(set(q['topic'] for q in available))
            selected_topic = st.selectbox("选择主题", topics, key="quiz_topic")
            available = [q for q in available if q['topic'] == selected_topic]

        selected = random.sample(available, min(n_questions, len(available)))
        st.session_state.quiz_questions = selected
        st.session_state.quiz_answers = {}

    questions = st.session_state.quiz_questions

    # 限时模式
    if quiz_mode == "限时挑战":
        time_limit = st.slider("时间限制(秒)", 30, 300, 120, key="quiz_time")
        elapsed = time.time() - st.session_state.quiz_start_time
        remaining = max(0, time_limit - elapsed)

        st.markdown(f"⏱️ 剩余时间：**{int(remaining // 60)}:{int(remaining % 60):02d}**")
        st.progress(remaining / time_limit)

        if remaining <= 0 and not st.session_state.quiz_submitted:
            st.session_state.quiz_submitted = True
            st.warning("⏰ 时间到！")

    st.markdown("---")

    for i, q in enumerate(questions):
        st.markdown(f"#### 第{i+1}题 [{q.get('topic', '')}] ({'⭐'*q['level']})")
        st.markdown(q['question'])

        answer = st.radio("选择答案", q['options'], key=f"quiz_q_{i}", index=None,
                         label_visibility="collapsed")
        if answer is not None:
            st.session_state.quiz_answers[i] = q['options'].index(answer)

        if st.session_state.get('quiz_submitted', False):
            user_ans = st.session_state.quiz_answers.get(i, -1)
            if user_ans == q['answer']:
                st.success(f"✅ {q['explanation']}")
            else:
                st.error(f"❌ 正确答案：{q['options'][q['answer']]}。{q['explanation']}")

        st.markdown("---")

    # 提交
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📝 提交测验", type="primary", key="quiz_submit_btn"):
            st.session_state.quiz_submitted = True

            correct = sum(1 for i, q in enumerate(questions)
                         if st.session_state.quiz_answers.get(i) == q['answer'])
            score_pct = correct / len(questions) * 100

            # 保存历史
            st.session_state.quiz_history.append({
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'score': correct,
                'total': len(questions),
                'mode': quiz_mode,
                'difficulty': difficulty
            })

            # 更新进度
            update_progress('知识测验', score_pct)

    with col2:
        if st.session_state.get('quiz_submitted', False):
            correct = sum(1 for i, q in enumerate(questions)
                         if st.session_state.quiz_answers.get(i) == q['answer'])
            score_pct = correct / len(questions) * 100

            st.markdown(f"## 🎯 成绩：{correct}/{len(questions)}（{score_pct:.0f}分）")

            if score_pct >= 80:
                st.success("🏆 优秀！仓库选址知识掌握扎实！")
                st.balloons()
            elif score_pct >= 60:
                st.warning("👍 良好！建议复习错题相关知识点。")
            else:
                st.error("📚 需加强！建议回到理论知识模块系统学习。")

            # 错题分析
            wrong_topics = [questions[i]['topic'] for i, q in enumerate(questions)
                          if st.session_state.quiz_answers.get(i) != q['answer']]
            if wrong_topics:
                st.markdown("#### 薄弱知识点")
                from collections import Counter
                topic_counts = Counter(wrong_topics)
                for topic, count in topic_counts.most_common():
                    st.markdown(f"- {topic}：错 {count} 题")

# ==================== 学习追踪 ====================
elif page == "📈 学习追踪":
    st.markdown('<div class="sub-header">📈 学习进度追踪</div>', unsafe_allow_html=True)

    st.markdown("### 🎓 掌握程度仪表盘")

    # 各模块进度
    modules = {
        '重心法': '重心法计算',
        '迭代重心法': '迭代重心法',
        '加权评分': '加权评分',
        '敏感度分析': '敏感度分析',
        '成本分析': '成本分析',
        '知识测验': '知识测验',
    }

    progress_cols = st.columns(3)
    for i, (display, key) in enumerate(modules.items()):
        score = st.session_state.learning_progress.get(key, 0)
        with progress_cols[i % 3]:
            color = '#4CAF50' if score >= 80 else '#FF9800' if score >= 60 else '#F44336'
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                <strong>{display}</strong>
                <div style="background:#eee; border-radius:5px; height:12px; margin:0.5rem 0;">
                    <div style="background:{color}; width:{score}%; height:100%; border-radius:5px;"></div>
                </div>
                <span style="font-size:0.9rem; color:{'#4CAF50' if score >= 60 else '#F44336'}">{score:.0f}%</span>
            </div>
            """, unsafe_allow_html=True)

    # 测验历史
    st.markdown("---")
    st.markdown("### 📊 测验成绩趋势")

    if st.session_state.quiz_history:
        hist_df = pd.DataFrame(st.session_state.quiz_history)
        hist_df['pct'] = hist_df['score'] / hist_df['total'] * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_df['date'], y=hist_df['pct'],
                                 mode='lines+markers',
                                 marker=dict(size=10),
                                 line=dict(width=2),
                                 name='成绩趋势'))
        fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="优秀线")
        fig.add_hline(y=60, line_dash="dash", line_color="orange", annotation_text="及格线")
        fig.update_layout(title="测验成绩趋势", yaxis_title="得分(%)",
                         yaxis=dict(range=[0, 105]), height=350)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 测验记录")
        st.dataframe(hist_df[['date', 'score', 'total', 'mode', 'difficulty']],
                    use_container_width=True)
    else:
        st.info("还没有测验记录，去完成一次测验吧！")

    # 学习建议
    st.markdown("---")
    st.markdown("### 💡 个性化学习建议")

    scores = st.session_state.learning_progress
    weak = [m for m, s in scores.items() if s < 60]
    strong = [m for m, s in scores.items() if s >= 80]

    if weak:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("#### ⚠️ 建议加强的模块")
        for w in weak:
            st.markdown(f"- **{w}**：当前掌握程度较低，建议回到对应模块练习")
        st.markdown('</div>', unsafe_allow_html=True)

    if strong:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("#### ✅ 已掌握的模块")
        for s in strong:
            st.markdown(f"- **{s}**：掌握良好，可以挑战更高级的练习")
        st.markdown('</div>', unsafe_allow_html=True)

    if not scores:
        st.info("开始学习后，系统将自动追踪你的掌握程度并给出个性化建议。")

# ==================== 关于系统 ====================
elif page == "ℹ️ 关于系统":
    st.markdown('<div class="sub-header">ℹ️ 关于系统</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 仓库选址教学系统 v2.0

    面向物流管理、供应链专业学生的**深度互动式教学平台**。

    #### 🆚 v1.0 → v2.0 升级内容
    """)

    upgrades = pd.DataFrame({
        '模块': ['重心法', '加权评分', '成本分析', '敏感度分析', '多方案对比',
                '仿真实验', '知识测验', '学习追踪'],
        'v1.0': ['基础一次计算', '固定权重评分', '简单加总', '无', '无',
                '无', '5题固定', '无'],
        'v2.0': ['+迭代收敛可视化', '+交互权重调整', '+盈亏平衡+全生命周期',
                '权重/需求/费率三维度', '雷达图+热力图', '蒙特卡洛仿真',
                '20题+随机+限时+分级', '进度仪表盘+建议']
    })
    st.dataframe(upgrades, use_container_width=True)

    st.markdown("#### 🛠️ 技术栈")
    st.markdown("- **前端**: Streamlit | **数据处理**: Pandas, NumPy | **可视化**: Plotly")

    st.markdown("---")
    st.markdown(f"#### 📅 系统信息")
    st.markdown(f"- 版本：2.0.0 | 开发时间：2026年5月 | 更新：{datetime.now().strftime('%Y-%m-%d')}")
    st.markdown("- 优化版新增：迭代重心法、敏感度分析、蒙特卡洛仿真、学习追踪等10+功能")

# ==================== 页脚 ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.85rem; padding: 1rem;'>
    仓库选址教学系统 v2.0 | 物流与供应链管理专业教学平台 | 2026
</div>
""", unsafe_allow_html=True)
