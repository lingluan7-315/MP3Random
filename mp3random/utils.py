#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 凌乱之主
# 2024年07月25日
"""
一些工具函数

- create_logger: 创建一个logger
- makedirs: 若文件夹不存在则创建文件夹，并返回标准化的路径
- time_from: 将时间秒数格式化为“0h0m0s”格式，若秒数小于0，则输出为0。
- time_list_from: 格式化时间列表，得到总时长（-h-m-s）格式、平均时长（-m-s）格式
"""
import logging
from os import path, makedirs


def create_logger(log_name: str = 'MP3Random', log_file: str = 'mp3random.log',
                  log_level: int = logging.DEBUG) -> logging.Logger:
    """
    创建一个logger

    :param log_name: logger的名字
    :param log_file: 日志文件的名字
    :param log_level: 日志的等级，包括DEBUG, INFO, WARNING, ERROR, CRITICAL
    :return: logger - 一个logger对象
    """
    # 创建一个logger
    logger = logging.getLogger(log_name)
    logger.setLevel(log_level)
    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    fh.setLevel(log_level)
    # 创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # 给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def create_path(path_name: str) -> str:
    """
    若文件夹不存在则创建文件夹，支持相对路径，支持多级文件夹，返回标准化的路径

    :param path_name: 要创建的目录
    :return: path_name - 创建的目录
    """
    path_name = path.normpath(path_name)
    if not path.exists(path_name):
        makedirs(path_name)
    return path_name


def time_from(second: float) -> str:
    """
    将时间秒数格式化为“0h0m0s”格式，若秒数小于0，则输出为0。

    :param second: 浮点型，时间秒数。
    :return: 字符串格式，时分秒格式的时间。
    """
    if second > 0:
        m, s = divmod(second, 60)
        h, m = divmod(m, 60)
    else:
        h = m = s = 0
    return '{:02.0f}h{:02.0f}m{:02.0f}s'.format(h, m, s)


def time_list_from(lists: list[float]) -> (str, str):
    """
    格式化时间列表，得到总时长（-h-m-s）格式、平均时长（-m-s）格式

    :param lists: 时间列表，单位为秒
    :return: 总时长（-h-m-s）格式、平均时长（-m-s）格式 的字符串
    """
    lists = [i for i in lists if i > 0]  # 去除列表中的负数
    if lists:  # 如果列表不为空
        m, s = divmod(sum(lists), 60)
        h, m = divmod(m, 60)
        mm, ss = divmod(sum(lists) / len(lists), 60)
    else:
        h = m = s = mm = ss = 0
    return '{:02.0f}:{:02.0f}:{:02.0f}'.format(h, m, s), '{:02.0f}:{:02.0f}'.format(mm, ss)


def check_dependence(dependence: str) -> bool:
    """
    检查依赖是否存在（如ffmpeg.exe、mp3gain.exe）

    :param dependence: 依赖的名称
    :return: 是否存在
    """
    # 检查当前文件夹下是否存在该依赖
    if path.exists(dependence):
        return True
    # 检查环境变量中是否存在该依赖
    elif path.exists(path.join(path.dirname(__file__), dependence)):
        return True
    else:
        return False


if __name__ == '__main__':
    print('utils')
