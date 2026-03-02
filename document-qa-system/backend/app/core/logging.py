"""
日志配置模块
统一的日志格式和配置管理
"""

import logging
import sys
from typing import Optional
from .config import settings


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """
    设置应用日志配置
    
    Args:
        level: 日志级别，默认使用配置中的级别
        
    Returns:
        配置好的logger实例
    """
    log_level = level or settings.LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 创建logger
    logger = logging.getLogger("document_qa")
    logger.setLevel(numeric_level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器到logger
    logger.addHandler(console_handler)
    
    return logger


# 全局logger实例
logger = setup_logging()