"""
初始化ChromaDB向量数据库
加载村落知识和设计案例数据
"""

import os
import sys
from pathlib import Path
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services import chromadb_service
from backend.core.config import settings


def load_text_files(directory: str) -> list:
    """
    加载目录下的所有文本文件
    
    Args:
        directory: 目录路径
        
    Returns:
        文件内容列表
    """
    files_data = []
    
    if not os.path.exists(directory):
        logger.warning(f"目录不存在: {directory}")
        return files_data
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    files_data.append({
                        'filename': filename,
                        'content': content
                    })
                logger.info(f"已加载文件: {filename}")
            except Exception as e:
                logger.error(f"加载文件失败 {filename}: {e}")
    
    return files_data


def init_villages_knowledge():
    """初始化村落知识库"""
    logger.info("=" * 60)
    logger.info("开始初始化村落知识库")
    logger.info("=" * 60)
    
    # 加载村落知识文件
    villages_dir = "./data/knowledge/villages"
    villages_files = load_text_files(villages_dir)
    
    if not villages_files:
        logger.warning("未找到村落知识文件，创建示例数据")
        return
    
    # 准备ChromaDB数据
    villages_data = []
    for i, file_data in enumerate(villages_files):
        # 从文件内容中提取村落名称
        content = file_data['content']
        lines = content.split('\n')
        village_name = "未知村落"
        province = "未知"
        
        for line in lines:
            if line.startswith('村落名称：'):
                village_name = line.replace('村落名称：', '').strip()
            elif line.startswith('所属地区：'):
                province = line.replace('所属地区：', '').strip().split('省')[0] + '省'
        
        villages_data.append({
            'id': f"village_{i+1:03d}",
            'content': content,
            'metadata': {
                'name': village_name,
                'province': province,
                'source': file_data['filename']
            }
        })
    
    # 添加到ChromaDB
    try:
        chromadb_service.add_villages(villages_data)
        logger.info(f"✅ 成功添加 {len(villages_data)} 个村落知识到ChromaDB")
    except Exception as e:
        logger.error(f"❌ 添加村落知识失败: {e}")


def init_design_cases():
    """初始化设计案例库"""
    logger.info("=" * 60)
    logger.info("开始初始化设计案例库")
    logger.info("=" * 60)
    
    # 加载设计案例文件
    cases_dir = "./data/knowledge/design_cases"
    cases_files = load_text_files(cases_dir)
    
    if not cases_files:
        logger.warning("未找到设计案例文件")
        return
    
    # 准备ChromaDB数据
    design_data = []
    for i, file_data in enumerate(cases_files):
        # 从文件内容中提取案例名称
        content = file_data['content']
        lines = content.split('\n')
        case_name = "未知案例"
        
        for line in lines:
            if line.startswith('设计案例：'):
                case_name = line.replace('设计案例：', '').strip()
                break
        
        design_data.append({
            'id': f"case_{i+1:03d}",
            'content': content,
            'metadata': {
                'name': case_name,
                'source': file_data['filename']
            }
        })
    
    # 添加到ChromaDB
    try:
        chromadb_service.add_design_cases(design_data)
        logger.info(f"✅ 成功添加 {len(design_data)} 个设计案例到ChromaDB")
    except Exception as e:
        logger.error(f"❌ 添加设计案例失败: {e}")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("ChromaDB初始化脚本")
    logger.info("=" * 60)
    
    # 初始化ChromaDB服务
    try:
        chromadb_service.initialize()
        logger.info("✅ ChromaDB服务初始化成功")
    except Exception as e:
        logger.error(f"❌ ChromaDB服务初始化失败: {e}")
        return
    
    # 询问是否重置数据库
    reset = input("\n是否重置现有数据库？(y/N): ").strip().lower()
    if reset == 'y':
        try:
            chromadb_service.reset_collections()
            logger.info("✅ 数据库已重置")
        except Exception as e:
            logger.error(f"❌ 数据库重置失败: {e}")
            return
    
    # 初始化村落知识库
    init_villages_knowledge()
    
    # 初始化设计案例库
    init_design_cases()
    
    # 显示统计信息
    logger.info("=" * 60)
    logger.info("初始化完成！统计信息：")
    logger.info("=" * 60)
    
    try:
        villages_count = chromadb_service.villages_collection.count()
        designs_count = chromadb_service.designs_collection.count()
        
        logger.info(f"村落知识库文档数: {villages_count}")
        logger.info(f"设计案例库文档数: {designs_count}")
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
    
    logger.info("=" * 60)
    
    # 测试检索
    test_search = input("\n是否测试检索功能？(y/N): ").strip().lower()
    if test_search == 'y':
        test_query = input("请输入检索关键词: ").strip()
        if test_query:
            try:
                results = chromadb_service.search_villages(test_query, n_results=2)
                logger.info(f"\n检索结果（共 {len(results['documents'])} 条）：")
                for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                    logger.info(f"\n结果 {i+1}:")
                    logger.info(f"村落: {metadata.get('name', '未知')}")
                    logger.info(f"内容预览: {doc[:200]}...")
            except Exception as e:
                logger.error(f"检索测试失败: {e}")


if __name__ == "__main__":
    main()

