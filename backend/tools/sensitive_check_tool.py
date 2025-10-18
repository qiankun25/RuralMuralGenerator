"""
敏感词检测工具
用于内容审核
"""

from langchain.tools import Tool
from typing import List, Set
from loguru import logger
import os

from core.config import settings


class SensitiveWordChecker:
    """敏感词检测器"""
    
    def __init__(self):
        """初始化敏感词检测器"""
        self.sensitive_words: Set[str] = set()
        self.load_sensitive_words()
    
    def load_sensitive_words(self):
        """加载敏感词库"""
        try:
            if os.path.exists(settings.sensitive_words_path):
                with open(settings.sensitive_words_path, 'r', encoding='utf-8') as f:
                    self.sensitive_words = set(line.strip() for line in f if line.strip())
                logger.info(f"已加载 {len(self.sensitive_words)} 个敏感词")
            else:
                # 创建默认敏感词库
                self._create_default_sensitive_words()
                logger.warning(f"未找到敏感词库，已创建默认敏感词库")
        except Exception as e:
            logger.error(f"加载敏感词库失败: {e}")
            self.sensitive_words = set()
    
    def _create_default_sensitive_words(self):
        """创建默认敏感词库"""
        default_words = [
            # 政治敏感词
            "暴力", "血腥", "恐怖",
            # 不当内容
            "色情", "赌博", "毒品",
            # 其他
            "迷信", "封建"
        ]
        
        os.makedirs(os.path.dirname(settings.sensitive_words_path), exist_ok=True)
        
        with open(settings.sensitive_words_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(default_words))
        
        self.sensitive_words = set(default_words)
    
    def check_text(self, text: str) -> dict:
        """
        检测文本中的敏感词
        
        Args:
            text: 待检测文本
            
        Returns:
            检测结果字典
        """
        if not settings.enable_content_review:
            return {
                "is_safe": True,
                "found_words": [],
                "message": "内容审核已禁用"
            }
        
        found_words = []
        
        for word in self.sensitive_words:
            if word in text:
                found_words.append(word)
        
        is_safe = len(found_words) == 0
        
        return {
            "is_safe": is_safe,
            "found_words": found_words,
            "message": "内容安全" if is_safe else f"检测到敏感词: {', '.join(found_words)}"
        }


# 创建全局检测器实例
checker = SensitiveWordChecker()


def check_sensitive_words(text: str) -> str:
    """
    检测敏感词（用于LangChain Tool）
    
    Args:
        text: 待检测文本
        
    Returns:
        检测结果的文本描述
    """
    try:
        result = checker.check_text(text)
        
        if result["is_safe"]:
            return "✅ 内容审核通过，未检测到敏感词"
        else:
            return f"⚠️ 内容审核警告：检测到敏感词 [{', '.join(result['found_words'])}]，建议修改"
            
    except Exception as e:
        logger.error(f"敏感词检测失败: {e}")
        return f"检测失败: {str(e)}"


# 创建LangChain Tool
sensitive_check_tool = Tool(
    name="check_sensitive_words",
    func=check_sensitive_words,
    description="""检测文本中的敏感词。
    输入：待检测的文本内容
    输出：审核结果，如果检测到敏感词会给出警告
    使用场景：在生成设计方案或文本内容后，使用此工具进行内容审核"""
)


if __name__ == "__main__":
    # 测试工具
    test_text = "这是一个关于传统文化的墙绘设计"
    result = check_sensitive_words(test_text)
    print(result)

