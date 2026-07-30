def parse_pokemon_data(data):
    """
    从原始API数据中提取并格式化关键信息
    """
    name = data["name"].capitalize()
    id_num = data["id"]
    
    # ===== 图片获取 =====
    image_url = data["sprites"]["other"]["official-artwork"]["front_default"]
    if not image_url:
        image_url = data["sprites"]["front_default"]
    if not image_url:
        image_url = data["sprites"]["other"]["dream_world"]["front_default"]
    if not image_url:
        image_url = "https://via.placeholder.com/200x200?text=No+Image"
    
    # ===== 类型 =====
    types = [t["type"]["name"].capitalize() for t in data["types"]]
    
    # ===== 身高体重 =====
    height = data["height"] / 10.0
    weight = data["weight"] / 10.0
    
    # ===== 能力值解析（关键修复） =====
    stat_mapping = {
        "hp": "HP",
        "attack": "Attack",
        "defense": "Defense",
        "special-attack": "Sp. Atk",
        "special-defense": "Sp. Def",
        "speed": "Speed"
    }
    
    stats = {}
    for stat_item in data["stats"]:
        stat_name = stat_item["stat"]["name"]
        stat_value = stat_item["base_stat"]
        display_name = stat_mapping.get(stat_name, stat_name.capitalize())
        stats[display_name] = stat_value
    
    # ===== 特性 =====
    abilities = [a["ability"]["name"].capitalize() for a in data["abilities"]]
    
    return {
        "name": name,
        "id": id_num,
        "image": image_url,
        "types": types,
        "height": height,
        "weight": weight,
        "stats": stats,
        "abilities": abilities,
        "total_stats": sum(stats.values())
    }