import streamlit as st
from datetime import datetime

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.header("📚 使用说明")
        st.markdown("""
        1. 输入宝可梦相关问题
        2. 点击搜索或按回车键
        3. 打开折叠卡查看详细信息
        
        **示例搜索词：**
        - `pikachu` / `皮卡丘`
        - `charizard` / `喷火龙`
        - `mewtwo` / `超梦`
        """)
        st.divider()
        st.caption(f"⚡ 数据来源: PokéAPI | {datetime.now().year}")