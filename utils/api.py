import requests
import streamlit as st
from data.pokemon_names import translate_name

@st.cache_data(ttl=3600)
def get_pokemon_data(name):
    """
    从 PokéAPI 获取宝可梦数据
    支持中英文输入，支持 Mega 形态
    """
    original = name.strip().lower()
    translated = translate_name(name)
    
    # 构建候选名称列表
    candidates = []
    
    # 1. 翻译后的名称
    if translated != original:
        candidates.append(translated)
        candidates.append(original)
    else:
        candidates.append(original)
    
    # 2. 处理 Mega 形态（有空格的情况）
    if " " in original:
        parts = original.split()
        if parts[0] == "mega" and len(parts) >= 2:
            base = parts[1] if len(parts) > 1 else parts[0]
            suffix = parts[2] if len(parts) > 2 else ""
            if suffix:
                candidates.append(f"{base}-mega-{suffix}")
            else:
                candidates.append(f"{base}-mega")
        elif len(parts) == 2:
            candidates.append("-".join(parts))
    
    # 去重
    candidates = list(set(candidates))
    
    # 尝试每个候选
    for search_name in candidates:
        url = f"https://pokeapi.co/api/v2/pokemon/{search_name}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                continue
            else:
                # 只打印日志，不显示给用户
                print(f"API 请求失败 (状态码: {response.status_code}) for {search_name}")
                continue
                
        except requests.exceptions.Timeout:
            print(f"请求超时: {search_name}")
            continue
        except requests.exceptions.ConnectionError:
            print(f"网络连接失败: {search_name}")
            continue
    
    # 所有候选都失败，返回 None
    return None