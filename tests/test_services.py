"""
服务层测试
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services import chromadb_service, llm_service


class TestChromaDBService:
    """测试ChromaDB服务"""
    
    def test_initialize(self):
        """测试初始化"""
        try:
            chromadb_service.initialize()
            assert chromadb_service.client is not None
            assert chromadb_service.villages_collection is not None
            print("✅ ChromaDB初始化测试通过")
        except Exception as e:
            pytest.fail(f"ChromaDB初始化失败: {e}")
    
    def test_search_villages(self):
        """测试村落知识库搜索"""
        try:
            chromadb_service.initialize()
            
            # 如果知识库为空，跳过测试
            if chromadb_service.villages_collection.count() == 0:
                pytest.skip("知识库为空，跳过搜索测试")
            
            results = chromadb_service.search_villages("徽派建筑", n_results=2)
            
            assert 'documents' in results
            assert 'metadatas' in results
            assert len(results['documents']) > 0
            
            print(f"✅ 搜索测试通过，找到 {len(results['documents'])} 个结果")
            
        except Exception as e:
            pytest.fail(f"搜索测试失败: {e}")


class TestLLMService:
    """测试LLM服务"""
    
    def test_generate_text(self):
        """测试文本生成"""
        # 注意：此测试需要配置API密钥
        if not llm_service.api_key:
            pytest.skip("未配置API密钥，跳过LLM测试")
        
        try:
            result = llm_service.generate_text("请用一句话介绍中国传统村落")
            
            assert result is not None
            assert len(result) > 0
            
            print(f"✅ LLM测试通过，生成文本: {result[:50]}...")
            
        except Exception as e:
            pytest.fail(f"LLM测试失败: {e}")


if __name__ == "__main__":
    # 运行测试
    print("=" * 60)
    print("开始测试服务层")
    print("=" * 60)
    
    # 测试ChromaDB
    test_chromadb = TestChromaDBService()
    test_chromadb.test_initialize()
    test_chromadb.test_search_villages()
    
    # 测试LLM
    test_llm = TestLLMService()
    test_llm.test_generate_text()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)

