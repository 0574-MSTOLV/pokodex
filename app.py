import streamlit as st
import aiohttp
import asyncio
import os

st.set_page_config(page_title="宝可梦AI助手", page_icon="🎯", layout="wide")

st.title("🎯 宝可梦AI助手")
st.markdown("输入宝可梦名称查询信息")

# ========== 直接调用 DeepSeek API ==========
async def simple_chat(prompt):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return "❌ 请设置 DEEPSEEK_API_KEY 环境变量"
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ API调用失败: {e}"

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# ========== 界面 ==========
prompt = st.text_input("输入宝可梦名称", placeholder="例如：皮卡丘、pikachu")

if prompt:
    with st.spinner("查询中..."):
        result = run_async(simple_chat(prompt))
        st.write(result)