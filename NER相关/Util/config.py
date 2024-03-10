import sys
sys.path.append('./Util')
import logging
import os
log_dir = './Log'

# 获取日志配置,返回日志加载器
def get_log_config(log_path):
    """
    获取日志配置
    :param log_path: 日志路径
    :return:
    """
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)  # 设置最低的日志级别
    log_path = os.path.join(log_dir,log_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
        print(f"日志路径已生成于{log_path}")
    else:
        print(f"日志路径已存在于{log_path}")

    info_path = os.path.join(log_path, 'Info.log')
    warning_path = os.path.join(log_path, 'Warning.log')
    error_path = os.path.join(log_path, 'Error.log')

    # 定义日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    class InfoFilter(logging.Filter):
        def filter(self, record):
            # 只允许INFO级别的日志记录通过过滤器
            return record.levelno == logging.INFO

    class WarningFilter(logging.Filter):
        def filter(self, record):
            # 只允许INFO级别的日志记录通过过滤器
            return record.levelno == logging.WARNING

    # 检查是否已存在相同配置的INFO级别处理器
    if not any(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler) and handler.level == logging.INFO):
        info_handler = logging.FileHandler(info_path, encoding='utf-8')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        info_handler.addFilter(InfoFilter())
        logger.addHandler(info_handler)

    # 检查是否已存在相同配置的WARNING级别处理器
    if not any(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler) and handler.level == logging.WARNING):
        warning_handler = logging.FileHandler(warning_path, encoding='utf-8')
        warning_handler.setLevel(logging.WARNING)
        warning_handler.setFormatter(formatter)
        warning_handler.addFilter(WarningFilter())
        logger.addHandler(warning_handler)

    # 检查是否已存在相同配置的ERROR级别处理器
    if not any(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler) and handler.level == logging.ERROR):
        error_handler = logging.FileHandler(error_path, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

    return logger

Corpus_log_config = get_log_config('Corpus')
json_log_config = get_log_config('Json')
