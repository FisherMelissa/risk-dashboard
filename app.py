import streamlit as st

# --- 1. 设置页面 ---
st.set_page_config(
    page_title="青少年风险分级干预系统",
    page_icon="⚖️",
    layout="wide"  # 使用宽屏布局
)

# --- 2. 核心函数：定义指标和计算逻辑 ---

# 您的13个指标
# 格式: "key": "在侧边栏显示的标签"
INDICATORS = {
    "jianhu": "1. 监护状况 (家庭)",
    "jiaoyang": "2. 教养方式 (家庭)",
    "gongneng": "3. 家庭功能 (家庭)",
    "renge": "4. 人格行为 (个体)",
    "renzhi": "5. 认知观念 (个体)",
    "ziwo": "6. 自我认同 (个体)",
    "tongban": "7. 同伴关系 (社会)",
    "shequ": "8. 社区环境 (社会)",
    "zaixiao": "9. 在校表现 (学校)",
    "fazhi": "10. 法治教育 (学校)",
    "xiguan": "11. 上网习惯 (网络)",
    "neirong": "12. 接触内容 (网络)",
    "jiaowang": "13. 线上交往 (网络)"
}

# 您的三个预警等级的干预措施
# (完全按照您的文档)
GREEN_ALERT = {
    "level": "🟩 绿色预警 (低风险 / 常规关注)",
    "description": "评估分数在安全阈值内，未成年人存在一些轻微的、偶发性的不良行为，但保护性因素较强，整体发展态势良好。",
    "core_measure": "以普适性预防为主。",
    "actions": [
        "系统自动将法治教育、网络安全、家庭教育等相关知识资源推送至家长和学校。",
        "法治副校长、社区工作者定期开展常规性的法治宣传和家庭教育指导讲座。",
        "此阶段重在提升整体环境的保护能力，无需针对个体的特殊干预。"
    ]
}

YELLOW_ALERT = {
    "level": "🟨 黄色预警 (中风险 / 重点关注)",
    "description": "评估分数超过安全阈值，风险因素显著增加或保护性因素明显减弱，出现持续性的不良行为（如逃学、夜不归宿、轻微欺凌），存在滑向违法犯罪的较大风险。",
    "core_measure": "启动早期、精准的社会干预。",
    "actions": [
        "**信息通报与会商：** 系统自动向所在学校、社区、民政、检察机关未检部门通报预警信息。相关部门启动联席会商机制。",
        "**启动“督促监护令”：** 若预警核心风险指向家庭监护缺失或不当，检察机关应依法启动社会调查，评估后向监护人发出“督促监护令”。",
        "**司法社工介入：** 由专业的司法社工对未成年人及其家庭进行深入的社会调查，制定个性化的帮扶计划，链接心理咨询、学业辅导等社会资源。"
    ]
}

RED_ALERT = {
    "level": "🟥 红色预警 (高风险 / 危机干预)",
    "description": "评估分数达到危险阈值，或已实施《预防未成年人犯罪法》中定义的严重不良行为，甚至已涉嫌犯罪。个体处于危机状态，亟需强力干预。",
    "core_measure": "启动多部门协同的危机干预。",
    "actions": [
        "**立即启动危机干预小组：** 由检察机关、公安机关牵头，联合教育、民政、卫健等部门组成危机干预小组，立即介入。",
        "**评估司法程序启动必要性：** 公安、检察机关根据其行为的违法或犯罪程度，评估是否需要立案侦查，启动司法程序。",
        "**专门矫治教育评估：** 对于已实施严重不良行为但未达刑事责任年龄或情节显著轻微的，由专门教育指导委员会评估决定是否送入专门学校。",
        "**启动“380”等综合社会救助机制：** 全面启动社会化综合救助，为处于危机中的未成年人提供覆盖生活、医疗、心理、就学、就业等全方位的兜底性保障。"
    ]
}

# --- 3. 构建界面 ---

# 标题
st.title("⚖️ 青少年风险动态评估与分级干预系统 (V3.2)")
st.markdown("---")

# 界面分为两栏：左边是输入，右边是输出
col1, col2 = st.columns(2)

# --- 左侧：输入面板 (个案评估) ---
with col1:
    st.header("1. 个案评估输入")
    st.markdown("请根据个案的**实际情况**，选择每个指标的状态。")
    
    # 我们用一个字典来存储所有 13 个选项的值
    scores = {}

    # 动态创建所有 13 个输入框
    for key, label in INDICATORS.items():
        # "风险" 得 1 分, "保护" 得 0 分
        scores[key] = st.radio(
            label,
            options=[0, 1],  # 0 是保护, 1 是风险
            format_func=lambda x: "风险 (Risk)" if x == 1 else "保护 (Protection)",
            horizontal=True # 水平排列
        )
    
    # "运行推演" 按钮
    run_button = st.button("生成干预策略", type="primary", use_container_width=True)

# --- 右侧：输出面板 (分级干预策略) ---
with col2:
    st.header("2. 评估结果与干预建议")

    if run_button:
        # 1. 计算总分
        total_score = sum(scores.values())
        
        # 2. 判定等级
        # (阈值设定：0-4 分为绿, 5-8 分为黄, 9-13 分为红)
        if total_score <= 4:
            alert = GREEN_ALERT
            st.success(alert["level"]) # 绿色框
        elif total_score <= 8:
            alert = YELLOW_ALERT
            st.warning(alert["level"]) # 黄色框
        else:
            alert = RED_ALERT
            st.error(alert["level"]) # 红色框
        
        # 3. 显示结果
        st.markdown(f"**综合风险积分：** {total_score} / 13 分")
        st.markdown(f"**情况描述：** {alert['description']}")
        
        st.subheader(f"核心措施：{alert['core_measure']}")
        
        st.subheader("具体行动建议：")
        # 逐条打印行动列表
        for i, action in enumerate(alert["actions"], 1):
            st.markdown(f"{i}. {action}")
            
    else:
        st.info("请在左侧面板完成个案评估，然后点击“生成干预策略”按钮。")
