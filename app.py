import streamlit as st
# 确保导入我们所有需要的库
import numpy as np
import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

# --- 1. 设置页面标题和布局 ---
st.set_page_config(
    page_title="青少年风险推演仪表盘",
    page_icon="⚖️",
    layout="centered" # 居中布局
)

# --- 2. 加载我们的贝叶斯网络模型 ---
# @st.cache_resource 确保模型只加载一次 (非常重要！)
@st.cache_resource
def build_bn_model():
    # (这是我们最终 V2.0 版本的 BN 模型)
    model = DiscreteBayesianNetwork([
        ('Parenting', 'Psychology'),
        ('Parenting', 'Peer'),
        ('Peer', 'Discipline'),
        ('Psychology', 'Discipline'),
        ('LawEdu', 'Discipline')
    ])

    cpd_p = TabularCPD(variable='Parenting', variable_card=2, values=[[0.6], [0.4]])
    cpd_l = TabularCPD(variable='LawEdu', variable_card=2, values=[[0.7], [0.3]])

    cpd_psy = TabularCPD(variable='Psychology', variable_card=2,
                         values=[[0.8, 0.3], [0.2, 0.7]],
                         evidence=['Parenting'], evidence_card=[2])

    cpd_peer = TabularCPD(variable='Peer', variable_card=2,
                          values=[[0.7, 0.4], [0.3, 0.6]],
                          evidence=['Parenting'], evidence_card=[2])

    # (Peer, Psy, Law) = (0,0,0),(0,0,1),...,(1,1,1)
    cpd_d = TabularCPD(variable='Discipline', variable_card=2,
                       values=[
                           [0.99, 0.8, 0.7, 0.4, 0.9, 0.6, 0.5, 0.2],
                           [0.01, 0.2, 0.3, 0.6, 0.1, 0.4, 0.5, 0.8]
                       ],
                       evidence=['Peer', 'Psychology', 'LawEdu'],
                       evidence_card=[2, 2, 2])

    model.add_cpds(cpd_p, cpd_l, cpd_psy, cpd_peer, cpd_d)

    if not model.check_model():
        raise ValueError("模型定义错误")

    print("贝叶斯网络模型已成功加载并准备就绪！")

    # 返回推断引擎
    return VariableElimination(model)

# --- 3. 构建 Streamlit 界面 ---

st.title("⚖️ 青少年风险情景推演")
st.markdown("通过干预不同维度的保护/风险因子，模拟对最终违纪风险的影响。")

# 加载模型
try:
    INFERENCE = build_bn_model()
except Exception as e:
    st.error(f"模型加载失败: {e}")
    st.stop() # 停止运行

st.header("1. 选择干预情景")

# 使用 format_func 来显示友好的选项名称
parenting_options_map = {
    1: "保持现状 (风险型)", # 1 是传给 pgmpy 的值
    0: "实施干预 (民主型)"  # 0 是传给 pgmpy 的值
}
parenting_option = st.selectbox(
    label="家庭教养方式 (干预):",
    options=list(parenting_options_map.keys()), # 选项是 [1, 0]
    format_func=lambda x: parenting_options_map[x] # 显示值
)

law_edu_options_map = {
    1: "保持现状 (缺乏)",
    0: "实施干预 (充足)"
}
law_edu_option = st.selectbox(
    label="法治教育 (干预):",
    options=list(law_edu_options_map.keys()), # 选项是 [1, 0]
    format_func=lambda x: law_edu_options_map[x] # 显示值
)

# --- 4. 运行推演 ---
if st.button("运行推演", type="primary", use_container_width=True):

    st.header("2. 推演结果")

    with st.spinner("正在调用 PGMpy 模型进行计算..."):
        # 1. 计算基线风险 (硬编码为 1,1)
        baseline_prob = INFERENCE.query(
            variables=['Discipline'], 
            evidence={'Parenting': 1, 'LawEdu': 1}
        )
        baseline_risk = baseline_prob.values[1] # P(Discipline=1)

        # 2. 计算干预后的情景风险
        scenario_prob = INFERENCE.query(
            variables=['Discipline'],
            evidence={'Parenting': parenting_option, 'LawEdu': law_edu_option}
        )
        scenario_risk = scenario_prob.values[1] # P(Discipline=1)

        # 3. 计算变化
        reduction = (baseline_risk - scenario_risk)
        reduction_pct = (reduction / baseline_risk) if baseline_risk > 0 else 0

        # 4. 显示漂亮的指标卡
        col1, col2, col3 = st.columns(3)
        col1.metric("基线风险", f"{baseline_risk * 100:.2f}%")
        col2.metric("干预后风险", f"{scenario_risk * 100:.2f}%", f"{reduction * 100:.2f}% (绝对降低)")
        col3.metric("风险降低比例", f"{reduction_pct * 100:.2f}%")

        st.success("推演计算完成！")
