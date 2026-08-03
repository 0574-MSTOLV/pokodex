import streamlit as st
from utils.api import get_pokemon_data
from utils.parser import parse_pokemon_data
from utils.ai import ai_understand, ai_describe, run_async
from components.sidebar import render_sidebar
from components.pokemon_card import render_pokemon_card

st.set_page_config(
    page_title="宝可梦AI助手",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 宝可梦AI助手")
st.markdown("输入宝可梦名称或描述特征，AI 帮你识别并展示信息")

render_sidebar()

# ========== 初始化状态 ==========
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pokemon_parsed" not in st.session_state:
    st.session_state.pokemon_parsed = None

# ========== 渲染历史消息 ==========
def render_messages():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and msg.get("pokemon_data"):
                with st.expander("📊 查看宝可梦详细信息", expanded=False):
                    render_pokemon_card(msg["pokemon_data"])

render_messages()

# ========== 显示当前宝可梦卡片 ==========
if st.session_state.pokemon_parsed:
    render_pokemon_card(st.session_state.pokemon_parsed)
    if st.button("🔄 重新查询", use_container_width=True):
        st.session_state.pokemon_parsed = None
        st.session_state.messages = []
        st.rerun()

# ========== 输入框 ==========
prompt = st.chat_input("输入宝可梦名称或描述特征...")

if prompt:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        # 先尝试直接查宝可梦
        data = get_pokemon_data(prompt)
        
        if data:
            # 直接匹配成功
            pokemon = parse_pokemon_data(data)
            st.session_state.pokemon_parsed = pokemon
            response = f"找到宝可梦：**{pokemon['name']}**！"
            st.write(response)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "pokemon_data": pokemon
            })
            st.rerun()
        else:
            # 用 AI 识别
            with st.spinner("🤔 正在识别..."):
                pokemon_name = run_async(ai_understand(prompt))
                
                if pokemon_name and pokemon_name != "unknown":
                    data = get_pokemon_data(pokemon_name)
                    if data:
                        pokemon = parse_pokemon_data(data)
                        st.session_state.pokemon_parsed = pokemon
                        
                        # 生成 AI 介绍（不使用 RAG）
                        description = run_async(ai_describe(data, prompt))
                        clean_answer = description.replace("~~", "") if description else f"这是 **{pokemon_name}**！"
                        
                        st.write(clean_answer)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": clean_answer,
                            "pokemon_data": pokemon
                        })
                        st.rerun()
                    else:
                        error_msg = f"找到 '{pokemon_name}'，但查不到数据 😅"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                        st.rerun()
                else:
                    error_msg = "没找到对应的宝可梦，换个描述试试？ 😊"
                    st.warning(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    st.rerun()