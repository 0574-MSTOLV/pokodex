import asyncio
from utils.api import get_pokemon_data
from utils.knowledge_writer import auto_add_to_knowledge_base
from utils.parser import parse_pokemon_data

def test():
    print("🔍 获取皮卡丘数据...")
    data = get_pokemon_data("pikachu")
    
    if data:
        print("✅ API 获取成功")
        pokemon = parse_pokemon_data(data)
        print(f"   名称: {pokemon['name']}")
        print(f"   编号: {pokemon['id']}")
        
        print("📝 写入知识库...")
        result = auto_add_to_knowledge_base(data, "测试查询")
        
        if result:
            print("✅ 知识库写入成功！")
        else:
            print("⚠️ 知识库写入失败（可能已存在）")
    else:
        print("❌ API 获取失败")

if __name__ == "__main__":
    test()