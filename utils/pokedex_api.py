import requests
import streamlit as st
from utils.api import get_pokemon_data

@st.cache_data(ttl=3600)
def get_pokemon_species(name):
    """获取宝可梦的物种信息（包含进化链、描述等）"""
    url = f"https://pokeapi.co/api/v2/pokemon-species/{name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=3600)
def get_evolution_chain(url):
    """获取进化链数据"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=3600)
def get_pokemon_moves(name, limit=20):
    """获取宝可梦可学的技能列表"""
    data = get_pokemon_data(name)
    if not data:
        return []
    
    moves = []
    for move_data in data.get("moves", [])[:limit]:
        move_name = move_data["move"]["name"].replace("-", " ").title()
        
        # 获取学习方式
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