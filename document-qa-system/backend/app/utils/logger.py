"""
日志配置
使用 structlog 进行结构化日志记录
"""
import logging
import sys
import structlog
from app.core.config import get_settings

settings = get_settings()


def setup_logging():
    """配置结构化日志"""
    
    # 配置标准 logging
    logging.basicConfig(
        format='%(message)s',
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        stream=sys.stdout
    )
    
    # 根据配置选择日志格式：console 或 json
    use_json_format = settings.LOG_FORMAT.lower() == "json" and not settings.DEBUG
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if use_json_format else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()
