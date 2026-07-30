import streamlit as st

def render_search():
    """
    渲染搜索框
    返回用户输入的名称
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        pokemon_name = st.text_input(
            "搜索宝可梦",
            placeholder="例如：pikachu 或 皮卡丘",
            label_visibility="collapsed"
        )
    
    with col2:
        search_clicked = st.button("🔍 搜索", use_container_width=True)
    
    return pokemon_name, search_clicked