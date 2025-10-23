import logging
from logging.handlers import RotatingFileHandler

def set_main_logger(log_path, console_level=logging.DEBUG, file_level=logging.WARNING):
    """
    设置主日志器，支持自定义控制台和文件的日志级别。

    参数:
        log_path (str): 日志文件路径
        console_level (int): 控制台日志等级，默认 logging.DEBUG
        file_level (int): 文件日志等级，默认 logging.WARNING

    返回:
        logging.Logger: 配置后的 logger 实例
    """
    logger = logging.getLogger()  # root logger
    logger.setLevel(min(console_level, file_level))  # 根 logger 应为最小等级以捕获全部信息

    for h in list(logger.handlers):
        logger.removeHandler(h)
        try:
            h.close()
        except Exception:
            pass

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)

    # 文件 handler
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=200 * 1024 * 1024,
        backupCount=1,
        encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [Thread:%(threadName)s - %(thread)d]\n%(message)s\n',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
