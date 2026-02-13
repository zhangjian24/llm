import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO"):
    """设置日志配置"""
    
    # 创建logs目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(formatter)
    
    # 错误文件处理器
    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # 配置特定模块的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("pinecone").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """获取命名日志记录器"""
    return logging.getLogger(name)