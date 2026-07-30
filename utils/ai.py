import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from utils.parser import parse_pokemon_data
from utils.api import get_pokemon_data
from utils.rag import ask_rag
from utils.knowledge_writer import auto_add_to_knowledge_base

load_dotenv()


# ============================================================
# 1. AI 识别宝可梦名称
# ============================================================
async def ai_understand(user_input):
    """调用大模型 API，理解用户想找什么宝可梦"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """你是一个宝可梦专家助手。
用户会用自然语言描述宝可梦，请从描述中提取宝可梦的英文名称。
如果用户直接输入了宝可梦名称（中英文都可以），直接返回英文名。
如果识别出多个宝可梦，返回最匹配的那一个。
只返回宝可梦的英文名，不要其他内容。"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"用户说：{user_input}\n请告诉我对应的宝可梦英文名称"}
    ]
    
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip().lower()
    except Exception as e:
        print(f"AI 理解失败: {e}")
        return None


# ============================================================
# 2. AI 生成宝可梦介绍
# ============================================================
async def ai_describe(pokemon_data, user_input):
    """根据宝可梦数据生成个性化介绍"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    pokemon = parse_pokemon_data(pokemon_data)
    
    prompt = f"""
用户想知道：{user_input}

宝可梦信息：
- 名字：{pokemon['name']}
- 图鉴编号：{pokemon['id']}
- 类型：{', '.join(pokemon['types'])}
- 身高：{pokemon['height']}m
- 体重：{pokemon['weight']}kg
- 特性：{', '.join(pokemon['abilities'])}
- 能力值：HP={pokemon['stats'].get('HP',0)}, 
  攻击={pokemon['stats'].get('Attack',0)}, 
  防御={pokemon['stats'].get('Defense',0)}, 
  特攻={pokemon['stats'].get('Sp. Atk',0)}, 
  特防={pokemon['stats'].get('Sp. Def',0)}, 
  速度={pokemon['stats'].get('Speed',0)}
- 种族值总和：{pokemon['total_stats']}

请用有趣、友好的语气介绍这只宝可梦，回答用户的问题。
回答要简短有力，控制在200字以内。
"""
    
    messages = [
        {"role": "system", "content": "你是一个热情的宝可梦专家，喜欢用生动的语言介绍宝可梦。"},
        {"role": "user", "content": prompt}
    ]
    
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"AI 描述失败: {e}")
        return None


# ============================================================
# 3. RAG 知识库问答（含自动填充 + 调试日志）
# ============================================================
async def ai_ask_with_rag(user_input):
    """
    使用 RAG 知识库回答用户问题
    如果知识库没有，调用 API 并自动填充到知识库
    """
    print(f"🔍 用户输入: {user_input}")
    
    # 1️⃣ 先尝试 RAG 知识库
    rag_answer, sources = ask_rag(user_input)
    print(f"📚 RAG 结果: {rag_answer is not None}, 来源数: {len(sources) if sources else 0}")
    
    if rag_answer and sources:
        print("✅ RAG 找到结果，直接返回")
        return rag_answer.replace("~~", "")
    
    # 2️⃣ RAG 没找到，调用 API
    print("🔄 RAG 无结果，调用 API...")
    pokemon_name = await ai_understand(user_input)
    print(f"🎯 AI 识别结果: {pokemon_name}")
    
    if pokemon_name and pokemon_name != "unknown":
        data = get_pokemon_data(pokemon_name)
        print(f"📦 API 数据: {data is not None}")
        if data:
            print("💾 准备写入知识库...")
            result = auto_add_to_knowledge_base(data, user_input)
            print(f"💾 写入结果: {result}")
            
            description = await ai_describe(data, user_input)
            return description.replace("~~", "") if description else f"这是 **{pokemon_name}**！"
    
    # 3️⃣ 都没有找到
    return "我没有找到相关信息，你可以试试搜索神奇宝贝百科 😊"


# ============================================================
# 4. 运行异步函数的辅助工具
# ============================================================
def run_async(coro):
    """在同步环境中运行异步函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)