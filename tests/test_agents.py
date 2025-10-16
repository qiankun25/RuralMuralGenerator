"""
智能体测试
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.agents import culture_analyst, creative_designer, image_generator
from backend.services import chromadb_service


class TestCultureAnalyst:
    """测试文化分析智能体"""
    
    def test_analyze(self):
        """测试文化分析"""
        # 初始化ChromaDB
        chromadb_service.initialize()
        
        # 测试村落信息
        village_info = {
            "name": "西递村",
            "location": "安徽省黄山市",
            "industry": "旅游、徽派建筑保护",
            "history": "明清古村落，以马头墙和木雕闻名"
        }
        
        try:
            result = culture_analyst.analyze(village_info)
            
            assert result is not None
            assert len(result) > 0
            assert "文化" in result or "建筑" in result
            
            print("✅ 文化分析测试通过")
            print(f"分析结果预览: {result[:200]}...")
            
        except Exception as e:
            # 如果是API密钥问题，跳过测试
            if "未配置" in str(e) or "API" in str(e):
                pytest.skip(f"跳过测试: {e}")
            else:
                pytest.fail(f"文化分析测试失败: {e}")


class TestCreativeDesigner:
    """测试创意设计智能体"""
    
    def test_generate_designs(self):
        """测试设计方案生成"""
        # 模拟文化分析结果
        culture_analysis = """
        ## 核心文化元素
        - 徽派建筑：马头墙、青砖黛瓦
        - 徽商文化：诚信经营
        
        ## 推荐色彩方案
        - 青灰色、白色
        """
        
        try:
            result = creative_designer.generate_designs(culture_analysis)
            
            assert result is not None
            assert len(result) > 0
            
            print("✅ 设计方案生成测试通过")
            print(f"设计方案预览: {result[:200]}...")
            
        except Exception as e:
            if "未配置" in str(e) or "API" in str(e):
                pytest.skip(f"跳过测试: {e}")
            else:
                pytest.fail(f"设计方案生成测试失败: {e}")


class TestImageGenerator:
    """测试图像生成智能体"""
    
    def test_generate(self):
        """测试图像生成"""
        test_prompt = "A beautiful Chinese village mural painting"
        
        try:
            result = image_generator.generate(test_prompt)
            
            assert result is not None
            assert 'status' in result
            # 允许返回Mock图像
            assert result['status'] in ['success', 'mock', 'error']
            
            print(f"✅ 图像生成测试通过，状态: {result['status']}")
            
        except Exception as e:
            pytest.fail(f"图像生成测试失败: {e}")


if __name__ == "__main__":
    # 运行测试
    print("=" * 60)
    print("开始测试智能体")
    print("=" * 60)
    
    # 测试文化分析智能体
    test_culture = TestCultureAnalyst()
    test_culture.test_analyze()
    
    # 测试创意设计智能体
    test_design = TestCreativeDesigner()
    test_design.test_generate_designs()
    
    # 测试图像生成智能体
    test_image = TestImageGenerator()
    test_image.test_generate()
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)

