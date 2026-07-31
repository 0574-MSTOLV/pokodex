import requests
import streamlit as st
from data.pokemon_names import translate_name

# ============================================================
# 1. 基础：获取宝可梦数据
# ============================================================
@st.cache_data(ttl=3600)
def get_pokemon_data(name):
    """
    从 PokéAPI 获取宝可梦数据
    支持中英文输入，支持 Mega 形态
    """
    original = name.strip().lower()
    translated = translate_name(name)
    
    candidates = []
    
    if translated != original:
        candidates.append(translated)
        candidates.append(original)
    else:
        candidates.append(original)
    
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
    
    candidates = list(set(candidates))
    
    for search_name in candidates:
        url = f"https://pokeapi.co/api/v2/pokemon/{search_name}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                continue
            else:
                print(f"API 请求失败 (状态码: {response.status_code}) for {search_name}")
                continue
                
        except requests.exceptions.Timeout:
            print(f"请求超时: {search_name}")
            continue
        except requests.exceptions.ConnectionError:
            print(f"网络连接失败: {search_name}")
            continue
    
    return None


# ============================================================
# 2. 进阶：获取物种信息（含进化链、描述）
# ============================================================
@st.cache_data(ttl=3600)
def get_pokemon_species(name):
    """
    获取宝可梦的物种信息（包含进化链、描述等）
    """
    # 先获取基础数据，确保名称有效
    base_data = get_pokemon_data(name)
    if not base_data:
        return None
    
    # 用 API 返回的 name 确保准确
    actual_name = base_data["name"]
    url = f"https://pokeapi.co/api/v2/pokemon-species/{actual_name}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


# ============================================================
# 3. 进阶：获取进化链
# ============================================================
@st.cache_data(ttl=3600)
def get_evolution_chain(url):
    """
    获取进化链数据
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


# ============================================================
# 4. 进阶：获取技能列表
# ============================================================
@st.cache_data(ttl=3600)
def get_pokemon_moves(name, limit=20):
    """
    获取宝可梦可学的技能列表
    """
    data = get_pokemon_data(name)
    if not data:
        return []
    
    moves = []
    for move_data in data.get("moves", [])[:limit]:
        move_name = move_data["move"]["name"].replace("-", " ").title()
        
        # 获取最新版本的学习方式
        for version_detail in move_data["version_group_details"]:
            if version_detail["version_group"]["name"] == "scarlet-violet":
                learn_method = version_detail["move_learn_method"]["name"].replace("-", " ")
                moves.append({
                    "name": move_name,
                    "learn_method": learn_method
                })
                break
        else:
            moves.append({
                "name": move_name,
                "learn_method": "其他方式"
            })
    
    return moves


# ============================================================
# 5. 进阶：获取完整宝可梦知识（组合函数）
# ============================================================
@st.cache_data(ttl=3600)
def get_pokemon_full_knowledge(name):
    """
    获取宝可梦的完整知识（基础数据 + 物种信息 + 技能）
    """
    base_data = get_pokemon_data(name)
    if not base_data:
        return None
    
    species_data = get_pokemon_species(name)
    moves = get_pokemon_moves(name, limit=15)
    
    result = {
        "base": base_data,
        "species": species_data,
        "moves": moves,
    }
    
    # 如果有进化链，获取详细数据
    if species_data:
        evolution_url = species_data.get("evolution_chain", {}).get("url")
        if evolution_url:
            result["evolution"] = get_evolution_chain(evolution_url)
    
    return result