import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'  # 🔽 添加这一行

import streamlit as st
import requests
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

VECTOR_DB_PATH = "./chroma_db"


@st.cache_resource
def get_embeddings_model():
    """获取嵌入模型"""
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


@st.cache_resource
def get_vector_store():
    """获取向量数据库客户端"""
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    return client


def build_knowledge_base():
    """构建知识库"""
    client = get_vector_store()
    
    existing_collections = client.list_collections()
    collection_names = [c.name for c in existing_collections]
    
    if "pokemon_knowledge" in collection_names:
        return client.get_collection("pokemon_knowledge")
    
    knowledge_dir = "./knowledge_base"
    if not os.path.exists(knowledge_dir):
        os.makedirs(knowledge_dir)
        return None
    
    all_texts = []
    for filename in os.listdir(knowledge_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(knowledge_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                paragraphs = content.split("\n\n")
                for para in paragraphs:
                    if len(para.strip()) > 20:
                        all_texts.append(para.strip())
    
    if not all_texts:
        return None
    
    collection = client.create_collection(
        name="pokemon_knowledge",
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
    )
    
    for i, text in enumerate(all_texts):
        collection.add(
            documents=[text],
            ids=[f"doc_{i}"]
        )
    
    return collection


def search_knowledge(question, top_k=3):
    """在知识库中搜索相关内容"""
    collection = build_knowledge_base()
    if collection is None:
        return []
    
    try:
        results = collection.query(
            query_texts=[question],
            n_results=top_k
        )
        
        if results and results['documents']:
            return results['documents'][0]
        return []
    except Exception as e:
        print(f"搜索失败: {e}")
        return []


def call_deepseek_api(prompt):
    """调用 DeepSeek API"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            print(f"API 错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"API 调用失败: {e}")
        return None


def ask_rag(question):
    """
    RAG 问答
    返回：(答案, 来源文档列表)
    """
    relevant_chunks = search_knowledge(question, top_k=3)
    
    if not relevant_chunks:
        return None, []
    
    context = "\n\n".join(relevant_chunks)
    prompt = f"""你是一个宝可梦专家助手。请根据以下知识库内容回答用户问题。

知识库内容：
{context}

用户问题：{question}

回答要求：
1. 只根据知识库内容回答
2. 如果知识库中没有相关信息，请说"我暂时还不知道"
3. 回答要友好、有趣

回答："""

    answer = call_deepseek_api(prompt)
    
    if answer:
        return answer, relevant_chunks
    return None, []