import os
from datetime import datetime
from utils.parser import parse_pokemon_data

KNOWLEDGE_BASE_DIR = "./knowledge_base"

def ensure_directory():
    """确保知识库目录存在"""
    os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)

def auto_add_to_knowledge_base(pokemon_data, user_input=None):
    """
    自动将 API 数据写入知识库
    
    Args:
        pokemon_data: 从 API 获取的原始数据
        user_input: 用户输入（可选，用于记录来源）
    
    Returns:
        bool: 是否写入成功
    """
    ensure_directory()
    
    # 解析数据
    pokemon = parse_pokemon_data(pokemon_data)
    name = pokemon["name"]
    
    # 检查是否已存在
    filepath = os.path.join(KNOWLEDGE_BASE_DIR, f"{name}.txt")
    if os.path.exists(filepath):
        print(f"📁 {name} 已在知识库中，跳过")
        return False
    
    # 生成知识库内容
    content = format_knowledge_entry(pokemon, user_input)
    
    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ 已自动添加到知识库: {name}")
    return True

def format_knowledge_entry(pokemon, user_input=None):
    """格式化知识库条目"""
    lines = []
    
    # 标题
    lines.append(f"【{pokemon['name']}】")
    lines.append("")
    
    # 基本信息
    lines.append(f"【图鉴编号】{pokemon['id']:04d}")
    lines.append(f"【属性】{', '.join(pokemon['types'])}")
    lines.append(f"【身高】{pokemon['height']:.1f} m")
    lines.append(f"【体重】{pokemon['weight']:.1f} kg")
    lines.append(f"【特性】{', '.join(pokemon['abilities'])}")
    lines.append("")
    
    # 能力值
    lines.append("【种族值】")
    for stat_name in ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]:
        value = pokemon["stats"].get(stat_name, 0)
        lines.append(f"  - {stat_name}: {value}")
    lines.append(f"  总计: {pokemon['total_stats']}")
    lines.append("")
    
    # 信息来源
    if user_input:
        lines.append(f"【来源】用户查询: {user_input}")
    lines.append(f"【更新时间】{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return "\n".join(lines)