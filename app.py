import streamlit as st
from utils.api import get_pokemon_data
from utils.parser import parse_pokemon_data
from utils.ai import ai_understand, ai_describe, ai_ask_with_rag, run_async
from components.sidebar import render_sidebar
from components.pokemon_card import render_pokemon_card

st.set_page_config(
    page_title="宝可梦AI助手",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 宝可梦AI助手")
st.markdown("提问关于宝可梦的问题，AI 会结合知识库回答")

render_sidebar()

# ========== 初始化状态 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_pokemon" not in st.session_state:
    st.session_state.current_pokemon = None

# ========== 渲染历史消息 ==========
def render_messages():
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and msg.get("pokemon_data"):
                with st.expander("📊 查看宝可梦详细信息", expanded=False):
                    render_pokemon_card(msg["pokemon_data"])

render_messages()

# ========== 输入框 ==========
prompt = st.chat_input("问关于宝可梦的问题...")

if prompt:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 先尝试直接查宝可梦
    data = get_pokemon_data(prompt)
    
    if data:
        # 如果直接匹配到宝可梦名，走基础流程
        pokemon = parse_pokemon_data(data)
        response = f"找到宝可梦：**{pokemon['name']}**！"
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "pokemon_data": pokemon
        })
        st.rerun()
    else:
        # 先用 AI 识别是哪只宝可梦
        with st.spinner("🤔 正在识别..."):
            pokemon_name = run_async(ai_understand(prompt))
            
            if pokemon_name and pokemon_name != "unknown":
                data = get_pokemon_data(pokemon_name)
                if data:
                    pokemon = parse_pokemon_data(data)
                    
                    # 使用知识库问答
                    with st.spinner("📚 检索知识库..."):
                        # 改成使用 RAG
                        answer = run_async(ai_ask_with_rag(prompt))
                        clean_answer = answer.replace("~~", "") if answer else f"这是 **{pokemon_name}**！"
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": clean_answer,
                        "pokemon_data": pokemon
                    })
                    st.rerun()
                else:
                    error_msg = f"找到 '{pokemon_name}'，但查不到数据 😅"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    st.rerun()
            else:
                error_msg = "没找到对应的宝可梦，换个描述试试？ 😊"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.rerun()