# -*- coding = utf-8 -*-
# @Time :2020/7/11 12:08 下午
# @Author: XZL
# @File : logger.py
# @Software: PyCharm
import logging
import os
import sys


def __singletion(cls):
    """
    单例模式的装饰器函数
    :param cls: 实体类
    :return: 返回实体类对象
    """
    instances = {}

    def getInstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getInstance


# 单例模式
@__singletion
class C_logger(object):
    def __init__(self, path, c_level=logging.DEBUG, f_level=logging.DEBUG):
        self.path = path
        self.c_level = c_level
        self.f_level = f_level

    # def get_logger(self):
    #     logger = logging.getLogger(self.path)
    #     logger.setLevel(logging.NOTSET)
    #     formatter = logging.Formatter("[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s]:%(message)s")
    #     # 设置日志文件
    #     file_handler = logging.FileHandler(self.path)
    #     file_handler.setFormatter(formatter)
    #
    #     # 控制台日志
    #     console_handler = logging.StreamHandler(sys.stdout)
    #     console_handler.setFormatter(formatter)
    #
    #     # 设置输出等级
    #     file_handler.setLevel(self.f_level)
    #     console_handler.setLevel(self.c_level)
    #
    #     logger.addHandler(console_handler)
    #     logger.addHandler(file_handler)
    #     return logger

    def get_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)

        # 第二步，建立一个fileHandler来把日志记录在文件里，级别为debug以上
        log_path = os.path.dirname(os.getcwd()) + '/'
        log_name = log_path + 'sys.log'
        logfile = log_name
        if not logger.handlers:
            fh = logging.FileHandler(self.path, mode='a')
            fh.setLevel(self.f_level)

            # 建立一个streamHandler来把日志打在CMD窗口上，级别为warning以上
            ch = logging.StreamHandler()
            ch.setLevel(self.c_level)  # 输出等级

            # 第三步，定义handler的输出格式 设置日志格式
            formatter = logging.Formatter("[%(asctime)s]-[%(filename)s:%(lineno)d]-%(levelname)s: %(message)s")
            fh.setFormatter(formatter)  # 文件
            ch.setFormatter(formatter)  # 控制台

            # 第四步，将logger添加到handler里面
            logger.addHandler(fh)
            logger.addHandler(ch)
        return logger


if __name__ == '__main__':
    log1 = C_logger('sys.log', logging.CRITICAL, logging.CRITICAL).get_logger()
    log2 = C_logger('sys.log', logging.CRITICAL, logging.CRITICAL).get_logger()
    print(log1 is log2)  #True

    log1.debug('一个debug信息')

    log1.info('一个info信息')

    log1.warning('一个warning信息')

    log1.error('一个error信息')

    log1.critical('一个致命critical信息')
