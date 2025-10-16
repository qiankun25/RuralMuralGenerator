"""
基础测试
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_import_config():
    """测试配置模块导入"""
    from backend.core.config import settings
    assert settings is not None
    assert hasattr(settings, 'dashscope_api_key')


def test_import_services():
    """测试服务模块导入"""
    from backend.services import chromadb_service, llm_service, image_service
    assert chromadb_service is not None
    assert llm_service is not None
    assert image_service is not None


def test_import_agents():
    """测试智能体模块导入"""
    from backend.agents import culture_analyst, creative_designer, image_generator
    assert culture_analyst is not None
    assert creative_designer is not None
    assert image_generator is not None


def test_import_tools():
    """测试工具模块导入"""
    from backend.tools import village_knowledge_tool, government_data_tool
    assert village_knowledge_tool is not None
    assert government_data_tool is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

