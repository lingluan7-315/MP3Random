#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 凌乱之主
# 2024年07月25日
from os.path import normpath

from mp3_operations import backup, to_mp3, mp3_clip, mp3_gain
from randomization import mp3_random
from utils import create_logger


def main():
    logger = create_logger()
    logger.info('开始运行')
    # 设置路径
    old_path = 'D:/0Python/LingLuan/MP3Random/other/音乐测试文件'
    music_path = 'D:/0Python/LingLuan/MP3Random/other/音乐文件'
    backup_path = 'D:/0Python/LingLuan/MP3Random/other/音乐备份'
    random_path = 'D:/0Python/LingLuan/MP3Random/other/音乐随机'
    txt_path = 'D:/0Python/LingLuan/MP3Random/other/音乐列表.txt'
    # 转换为normal路径
    old_path = normpath(old_path)
    music_path = normpath(music_path)
    backup_path = normpath(backup_path)
    random_path = normpath(random_path)
    txt_path = normpath(txt_path)
    # 备份
    backup(old_path, backup_path, logger)
    # 转换为 MP3
    to_mp3(old_path, music_path, logger, remove_flag=False)
    # 切片
    mp3_clip(music_path, music_path, logger)
    # 音量调整
    mp3_gain(music_path, 99, logger, '../other/mp3gain.exe')
    # 备份
    backup(music_path, backup_path, logger)
    # 随机排列
    mp3_random(music_path, random_path, txt_path, logger)
    logger.info('运行结束')


if __name__ == '__main__':
    main()
