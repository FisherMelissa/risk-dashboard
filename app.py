import streamlit as st

# --- 1. 设置页面 ---
st.set_page_config(
    page_title="青少年风险分级干预系统 (V3.3)",
    page_icon="⚖️",
    layout="wide"  # 必须使用宽屏布局
)

# --- 2. 核心数据结构 (V3.3 - 基于您的具体指标) ---

# 您的13个维度，以及每个维度下的具体风险/保护指标
INDICATORS = {
    "jianhu": {
        "label": "1. 监护状况 (家庭)",
        "risks": ["留守", "流动", "单亲", "事实无人抚养"],
        "protections": ["监护稳定且到位"]
    },
    "jiaoyang": {
        "label": "2. 教养方式 (家庭)",
        "risks": ["暴力型教养", "溺爱型教养", "忽视型教养"],
        "protections": ["权威/民主型教养", "亲子沟通良好"]
    },
    "gongneng": {
        "label": "3. 家庭功能 (家庭)",
        "risks": ["严重家庭冲突", "家庭成员有犯罪史"],
        "protections": ["家庭氛围和谐", "家庭支持系统强"]
    },
    "renge": {
        "label": "4. 人格行为 (个体)",
        "risks": ["冲动控制差", "攻击性强", "情绪不稳定"],
        "protections": ["情绪调节能力强", "有同理心"]
    },
    "renzhi": {
        "label": "5. 认知观念 (个体)",
        "risks": ["价值观扭曲", "法治意识淡薄", "存在不良行为史"],
        "protections": ["认同社会规范", "有明确的是非观"]
    },
    "ziwo": {
        "label": "6. 自我认同 (个体)",
        "risks": ["低自尊", "学业失败感强"],
        "protections": ["拥有特长", "获得成就感", "积极的自我评价"]
    },
    "tongban": {
        "label": "7. 同伴关系 (社会)",
        "risks": ["结交不良同伴", "加入不良群体"],
        "protections": ["拥有积极、支持性的同伴圈"]
    },
    "shequ": {
        "label": "8. 社区环境 (社会)",
        "risks": ["居住社区治安差", "周边不良场所多"],
        "protections": ["社区凝聚力强", "文化活动丰富"]
    },
    "zaixiao": {
        "label": "9. 在校表现 (学校)",
        "risks": ["逃学", "辍学", "频繁违纪"],
        "protections": ["积极参与学校活动", "师生关系良好"]
    },
    "fazhi": {
        "label": "10. 法治教育 (学校)",
        "risks": ["缺乏系统性法治教育"],
        "protections": ["定期接受法治教育", "参与模拟法庭等活动"]
    },
    "xiguan": {
        "label": "11. 上网习惯 (网络)",
        "risks": ["上网时间过长", "深夜上网", "沉迷游戏"],
        "protections": ["上网行为有节制", "内容健康"]
    },
    "neirong": {
        "label": "12. 接触内容 (网络)",
        "risks": ["频繁接触暴力/色情", "接触极端言论"],
        "protections": ["主要浏览学习/兴趣类内容"]
    },
    "jiaowang": {
        "label": "13. 线上交往 (网络)",
        "risks": ["参与网络欺凌", "接触网络黑灰产"],
        "protections": ["线上社交关系健康"]
    }
}

# 您的三个预警等级的干预措施 (不变)
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

st.title("⚖️ 青少年风险动态评估与分级干预系统 (V3.3)")
st.markdown("---")

col1, col2 = st.columns([1, 1]) # 两栏 1:1 分配

# --- 左侧：输入面板 (个案评估) ---
with col1:
    st.header("1. 个案评估输入 (多指标交叉版)")
    st.markdown("请根据个案的**实际情况**，**勾选**所有符合的指标。")

    # V3.3 核心：使用 st.session_state 存储所有复选框的状态
    if 'scores' not in st.session_state:
        st.session_state.scores = {}

    total_risk_factors_selected = 0
    total_protection_factors_selected = 0

    # 动态创建所有 13 个折叠菜单
    for key, data in INDICATORS.items():
        with st.expander(f"**{data['label']}**"):
            
            # 组织布局：风险在左，保护在右
            r_col, p_col = st.columns(2)
            
            with r_col:
                st.subheader("风险因素 (Risk)")
                for item in data['risks']:
                    # 唯一的 key，例如 "jianhu_risk_留守"
                    item_key = f"{key}_risk_{item}"
                    if item_key not in st.session_state.scores:
                         st.session_state.scores[item_key] = False # 默认不勾选
                    
                    # 创建复选框，并将其状态绑定到 session_state
                    st.session_state.scores[item_key] = st.checkbox(item, key=item_key)
                    if st.session_state.scores[item_key]:
                        total_risk_factors_selected += 1
                        
            with p_col:
                st.subheader("保护因素 (Protection)")
                for item in data['protections']:
                    item_key = f"{key}_protection_{item}"
                    if item_key not in st.session_state.scores:
                         st.session_state.scores[item_key] = False
                         
                    st.session_state.scores[item_key] = st.checkbox(item, key=item_key)
                    if st.session_state.scores[item_key]:
                        total_protection_factors_selected += 1

    st.markdown("---")
    # “运行推演” 按钮
    run_button = st.button("生成干预策略", type="primary", use_container_width=True)


# --- 右侧：输出面板 (分级干预策略) ---
with col2:
    st.header("2. 评估结果与干预建议")

    if run_button:
        # 1. 计算总分 (V3.3 净风险积分)
        # (我们已经在左侧的渲染中计算了 total_risk/protection_factors_selected)
        net_risk_score = total_risk_factors_selected - total_protection_factors_selected
        
        # 2. 判定等级 (V3.3 新阈值)
        if net_risk_score <= 1:
            alert = GREEN_ALERT
            st.success(alert["level"]) # 绿色框
        elif net_risk_score <= 6:
            alert = YELLOW_ALERT
            st.warning(alert["level"]) # 黄色框
        else: # net_risk_score >= 7
            alert = RED_ALERT
            st.error(alert["level"]) # 红色框
        
        # 3. 显示结果
        st.metric("综合净风险积分", f"{net_risk_score:+d} 分", 
                  f"（{total_risk_factors_selected}个风险因素 - {total_protection_factors_selected}个保护因素）")
        st.markdown(f"**情况描述：** {alert['description']}")
        
        st.subheader(f"核心措施：{alert['core_measure']}")
        
        st.subheader("具体行动建议：")
        # 逐条打印行动列表
        for i, action in enumerate(alert["actions"], 1):
            st.markdown(f"{i}. {action}")
            
    else:
        st.info("请在左侧面板完成个案评估（勾选所有符合的指标），然后点击“生成干预策略”按钮。")
