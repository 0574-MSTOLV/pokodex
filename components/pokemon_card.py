import streamlit as st
import pandas as pd
from data.pokemon_names import get_type_color

def render_pokemon_card(pokemon):
    """渲染宝可梦信息卡片"""
    
    st.divider()
    
    # ---- 主信息区域 ----
    info_col, detail_col = st.columns([1, 2])
    
    with info_col:
        st.image(pokemon["image"], use_container_width=True)
        if "placeholder" in pokemon["image"]:
            st.caption("⚠️ 图片加载失败")
    
    with detail_col:
        st.subheader(f"#{pokemon['id']:04d} {pokemon['name']}")
        
        # 类型标签
        type_html = " ".join([
            f'<span style="background-color:{get_type_color(t)};'
            f'color:white;padding:4px 14px;border-radius:12px;font-weight:bold;">{t}</span>'
            for t in pokemon["types"]
        ])
        st.markdown(f"**类型:** {type_html}", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        col_a.metric("📏 身高", f"{pokemon['height']:.1f} m")
        col_b.metric("⚖️ 体重", f"{pokemon['weight']:.1f} kg")
        
        st.markdown(f"**特性:** {', '.join(pokemon['abilities'])}")
    
    # ---- 能力值区域（修复版） ----
    st.subheader("📊 能力值")
    
    # 定义顺序和对应的中文名称
    stat_order = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    stat_names_cn = ["HP", "攻击", "防御", "特攻", "特防", "速度"]  # 对应的中文
    
    stat_values = []
    for stat_name in stat_order:
        value = pokemon["stats"].get(stat_name, 0)
        stat_values.append(value)
    
    # 检查是否有数据
    if sum(stat_values) > 0:
        # 用中文名称作为 X 轴标签
        chart_data = pd.DataFrame({
            "能力": stat_names_cn,  # ← 这里用中文名称
            "数值": stat_values
        })
        st.bar_chart(chart_data.set_index("能力"))
        
        # 详细数值卡片（显示英文名称，更直观）
        st.caption("📊 详细数值")
        cols = st.columns(6)
        for i, (name_en, name_cn, value) in enumerate(zip(stat_order, stat_names_cn, stat_values)):
            with cols[i]:
                # 显示中文名称
                st.metric(name_cn, value)
                progress_value = min(value / 255, 1.0)
                st.progress(progress_value)
        
        st.info(f"✨ **种族值总和**: {pokemon['total_stats']}")
    else:
        st.warning("⚠️ 未能获取能力值数据")

def render_hot_pokemon():
    """渲染热门宝可梦快捷入口"""
    st.divider()
    st.caption("🔥 热门宝可梦")
    
    popular = ["皮卡丘", "喷火龙", "超梦", "伊布", "卡比兽", "耿鬼"]
    popular_cols = st.columns(len(popular))
    
    for i, name in enumerate(popular):
        if popular_cols[i].button(name, use_container_width=True):
            st.session_state["pokemon_name"] = name
            st.rerun()