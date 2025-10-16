#!/usr/bin/env python3
"""
项目完整性检查脚本
检查所有模块是否可以正常导入和运行
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_imports():
    """检查关键模块导入"""
    print("=" * 60)
    print("检查模块导入")
    print("=" * 60)
    
    checks = [
        ("配置模块", "backend.core.config", "settings"),
        ("ChromaDB服务", "backend.services.chromadb_service", "ChromaDBService"),
        ("LLM服务", "backend.services.llm_service", "LLMService"),
        ("图像服务", "backend.services.image_service", "ImageGenerationService"),
        ("政府API服务", "backend.services.government_service", "GovernmentDataService"),
        ("文化分析智能体", "backend.agents.culture_analyst", "CultureAnalystAgent"),
        ("创意设计智能体", "backend.agents.creative_designer", "CreativeDesignerAgent"),
        ("图像生成智能体", "backend.agents.image_generator", "ImageGeneratorAgent"),
        ("CrewAI管理器", "backend.agents.crew_manager", "CrewManager"),
        ("API路由", "backend.api.routes", "router"),
        ("API模型", "backend.api.models", "VillageInfo"),
    ]
    
    success_count = 0
    total_count = len(checks)
    
    for name, module_path, attr_name in checks:
        try:
            module = __import__(module_path, fromlist=[attr_name])
            getattr(module, attr_name)
            print(f"✅ {name}: 导入成功")
            success_count += 1
        except ImportError as e:
            print(f"❌ {name}: 导入失败 - {e}")
        except AttributeError as e:
            print(f"⚠️ {name}: 模块导入成功但属性缺失 - {e}")
        except Exception as e:
            print(f"❌ {name}: 未知错误 - {e}")
    
    print(f"\n导入检查完成: {success_count}/{total_count} 成功")
    return success_count == total_count


def check_files():
    """检查关键文件是否存在"""
    print("\n" + "=" * 60)
    print("检查关键文件")
    print("=" * 60)
    
    required_files = [
        "requirements.txt",
        ".env.example",
        "README.md",
        "backend/main.py",
        "backend/__init__.py",
        "backend/core/__init__.py",
        "backend/core/config.py",
        "backend/services/__init__.py",
        "backend/services/chromadb_service.py",
        "backend/services/llm_service.py",
        "backend/services/image_service.py",
        "backend/services/government_service.py",
        "backend/tools/__init__.py",
        "backend/tools/chromadb_tool.py",
        "backend/tools/government_api_tool.py",
        "backend/tools/sensitive_check_tool.py",
        "backend/agents/__init__.py",
        "backend/agents/culture_analyst.py",
        "backend/agents/creative_designer.py",
        "backend/agents/image_generator.py",
        "backend/agents/crew_manager.py",
        "backend/api/__init__.py",
        "backend/api/models.py",
        "backend/api/routes.py",
        "frontend/__init__.py",
        "frontend/app.py",
        "scripts/init_chromadb.py",
        "scripts/setup.bat",
        "scripts/start_backend.bat",
        "scripts/start_frontend.bat",
        "data/knowledge/villages/village_001.txt",
        "data/knowledge/villages/village_002.txt",
        "data/knowledge/design_cases/case_001.txt",
        "data/knowledge/design_cases/case_002.txt",
        "data/sensitive_words.txt",
        "tests/__init__.py",
        "tests/test_basic.py",
        "tests/test_services.py",
        "tests/test_agents.py",
        "docs/API.md",
        "docs/SETUP.md",
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}: 文件不存在")
            missing_files.append(file_path)
    
    print(f"\n文件检查完成: {len(required_files) - len(missing_files)}/{len(required_files)} 存在")
    
    if missing_files:
        print("\n缺失的文件:")
        for file_path in missing_files:
            print(f"  - {file_path}")
    
    return len(missing_files) == 0


def check_directories():
    """检查目录结构"""
    print("\n" + "=" * 60)
    print("检查目录结构")
    print("=" * 60)
    
    required_dirs = [
        "backend",
        "backend/core",
        "backend/services",
        "backend/tools",
        "backend/agents",
        "backend/api",
        "frontend",
        "scripts",
        "data",
        "data/knowledge",
        "data/knowledge/villages",
        "data/knowledge/design_cases",
        "data/mock_images",
        "tests",
        "docs",
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/: 目录不存在")
            missing_dirs.append(dir_path)
    
    print(f"\n目录检查完成: {len(required_dirs) - len(missing_dirs)}/{len(required_dirs)} 存在")
    
    if missing_dirs:
        print("\n缺失的目录:")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}/")
    
    return len(missing_dirs) == 0


def check_config():
    """检查配置"""
    print("\n" + "=" * 60)
    print("检查配置")
    print("=" * 60)
    
    try:
        from backend.core.config import settings
        
        print(f"✅ 配置加载成功")
        print(f"  - ChromaDB路径: {settings.chromadb_path}")
        print(f"  - LLM模型: {settings.llm_model_name}")
        print(f"  - 图像输出目录: {settings.image_output_dir}")
        
        # 检查API密钥配置
        if settings.dashscope_api_key:
            print(f"✅ DashScope API密钥已配置")
        else:
            print(f"⚠️ DashScope API密钥未配置")
        
        if settings.government_api_key:
            print(f"✅ 政府API密钥已配置")
        else:
            print(f"⚠️ 政府API密钥未配置（将使用Mock数据）")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False


def main():
    """主函数"""
    print("🏡 乡村墙绘AI生成系统 - 项目完整性检查")
    print(f"项目路径: {project_root}")
    
    # 执行所有检查
    checks = [
        ("目录结构", check_directories),
        ("关键文件", check_files),
        ("模块导入", check_imports),
        ("配置检查", check_config),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name}检查失败: {e}")
            results.append((check_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("检查总结")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查通过！项目已准备就绪。")
        print("\n下一步操作:")
        print("1. 配置API密钥: 编辑 .env 文件")
        print("2. 初始化知识库: python scripts/init_chromadb.py")
        print("3. 启动后端: scripts/start_backend.bat")
        print("4. 启动前端: scripts/start_frontend.bat")
    else:
        print("\n⚠️ 部分检查未通过，请根据上述信息修复问题。")
        print("\n建议操作:")
        print("1. 运行 pip install -r requirements.txt 安装依赖")
        print("2. 检查缺失的文件和目录")
        print("3. 配置必要的API密钥")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
