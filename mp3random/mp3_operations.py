#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 凌乱之主
# 2024年07月25日
"""
MP3 文件操作

- backup: 备份文件夹
- to_mp3: 将各种格式转换为 mp3 格式
- mp3_clip: 将音乐文件进行切片
- mp3_gain: 将音乐文件的音量调整到相应的分贝数
"""
import logging
from os import listdir, sep, remove, path
from re import match
from shutil import copytree, rmtree, copy
from subprocess import run, CREATE_NO_WINDOW

# TODO: mutagen库是GPL开源协议的，尝试使用其他库
from mutagen.mp3 import MP3

from utils import create_path, update_progress


def backup(input_path: str, output_path: str, logger: logging.Logger) -> bool:
    """
    备份文件夹

    :param input_path: 输入文件夹（需要备份的文件夹路径）
    :param output_path: 输出文件夹（备份后文件夹的路径）
    :param logger: 日志对象
    :return: 是否备份成功
    """
    # 提取需要备份呢的文件夹的最后一级名称作为新的文件夹的名称
    name = path.basename(input_path)
    backup_place = path.join(output_path, name)
    backup_place = path.normpath(backup_place)
    # 若该文件夹已存在则删除该文件夹
    if path.exists(backup_place):
        rmtree(backup_place)
        logger.info(f'删除已存在的备份文件夹：{backup_place}')
    # 复制整个文件夹
    try:
        copytree(input_path, backup_place)
        logger.info(f'备份文件夹：{input_path} -> {backup_place}')
    except Exception as e:
        logger.error(f'备份文件夹 {input_path} 失败：{e}')
        return False
    return True


def to_mp3(input_path: str, output_path: str, logger: logging.Logger, process_inner_list: list,
           ffmpeg_path: str = 'ffmpeg.exe', remove_flag: bool = True):
    """
    调用 ffmpeg.exe 将各种格式转换为 mp3 格式

    :param input_path: 输入文件夹（转换前音乐文件所在的路径）
    :param output_path: 输出文件夹（转换后音乐文件所在的路径）
    :param logger: 日志记录器
    :param process_inner_list: 进度条控件列表
    :param ffmpeg_path: ffmpeg.exe 文件的路径，默认为 'ffmpeg.exe'
    :param remove_flag: 是否删除原文件，默认为 True
    """
    # 转换为 normal 路径
    input_path = path.normpath(input_path)
    output_path = path.normpath(output_path)

    # 读取文件列表
    old_files = listdir(input_path)
    count = len(old_files)
    if old_files:  # 如果读取的文件列表不为空
        for i, old_file in enumerate(old_files):
            # 记录两个文件名作为更新正在操作文件的依据
            t = old_file.rfind('.')
            new_file = old_file[:t] + '.mp3'
            # 组合完整路径
            old = input_path + sep + old_file  # 旧文件的完整路径
            new = create_path(output_path) + sep + new_file  # 新文件的完整路径，位于music_path文件夹且添加MP3后缀
            # 更新进度条
            update_progress(process_inner_list, i + 1, count, old_file, new_file)
            try:
                # 用 ffmpeg.exe 将其转化到新位置的 MP3 ，并设定码率为 128k
                # 文件名两侧加上 “ ，可以防止 ffmpeg.exe 不识别空格、冒号等字符，使用 -y 参数可以覆盖同名文件
                # 采用 subprocess.run 调用 ffmpeg.exe 进行音乐转换，不调用命令行
                result = run(f'"{ffmpeg_path}" -i "{old}" -b:a 128k "{new}" -y',
                             capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW)
                if result.returncode == 0:  # 如果转换成功
                    logger.info(f'转换文件：{old} -> {new}')
                    if remove_flag:
                        remove(old)
                        logger.info(f'删除旧文件：{old}')
                else:  # 如果转换失败
                    logger.error(f'转换失败：{old} -> {new}， {result.stderr}')
            except FileNotFoundError:
                logger.error(f'转换失败：ffmpeg.exe 未找到')
    else:  # 如果读取的文件列表为空
        logger.warning(f'音乐文件夹 {input_path} 为空')


def _re_name(files: list[(str, float)]):
    """
    将文件名中的文件名部分和需切片部分提取出来，并判断是否需要切片

    :param files: 需要进行判断的文件列表
    :return: (需要切片的文件列表: [旧文件名，新文件名，切片起始时间，切片结束时间], 需要重命名的文件列表: [旧文件名，新文件名])
    :rtype: (list[str, str, float | None, float | None], list[str, str])
    """
    # 获取需要切片的文件名称
    clip_need = []  # 初始化列表作为需要操作的内容
    rename_need = []  # 初始化列表作为需要重命名的内容
    used_name = ['']  # 已有的文件名列表
    for file, length in files:  # 遍历文件列表
        m = match('(.*)[(（](-{0,1}?[^-]*?)-(-{0,1}?[^-]*?)[)）](.*)\..*', file)  # 正则提取各部分
        # 如果文件名中含有括号
        if m:
            name = m.group(1) + m.group(4)  # 将去除括号和后缀名后的部分作为新的名称
            st = m.group(2)
            try:  # 如果提取出数字则作为切片时间，否则设置为None
                sta = float(st)
            except ValueError:
                sta = None
            en = m.group(3)
            try:
                end = float(en)
            except ValueError:
                end = None

            # 如果名称为空或已存在则添加后缀
            while name in used_name:
                name = name + '_2'
            used_name.append(name)  # 记录已有的文件名

            name = name + '.mp3'  # 为新的文件名添加后缀
            # 如果起止时间都是None，重命名文件
            if sta == end is None:
                rename_need.append([file, name])  # 记录需要重命名的文件列表
            else:  # 否则将该文件的各项信息添加到列表中
                # 读取音乐长度并将负数和None值转化为可以操作的音乐长度
                if sta and sta < 0:
                    sta = length + sta
                elif not sta:
                    sta = 0
                if end and end < 0:
                    end = length + end
                elif not end:
                    end = length

                if sta > end:  # 如果起始时间大于结束时间则交换两者
                    sta, end = end, sta
                if sta < 0:  # 如果起始时间小于0则设置为0
                    sta = 0
                if end > length:  # 如果结束时间大于音乐长度则设置为音乐长度
                    end = length

                # 如果起始时间等于结束时间或等于音乐长度或结束时间等于0则将其视为无效切片
                if sta == end or sta >= length or end <= 0:
                    continue

                clip_need.append([file, name, sta, end])
        # 否则不进行操作
        else:
            pass
    return clip_need, rename_need


def mp3_clip(input_path: str, output_path: str, logger: logging.Logger, process_inner_list: list,
             ffmpeg_path: str = 'ffmpeg.exe', remove_flag: bool = True):
    """
    调用 ffmpeg.exe 进行音乐切片

    :param input_path: 输入文件夹（需要切片的音乐文件所在的路径）
    :param output_path: 输出文件夹（切片后音乐文件所在的路径）
    :param logger: 日志记录器
    :param process_inner_list: 进度条控件列表
    :param ffmpeg_path: ffmpeg.exe 文件的路径，默认为 'ffmpeg.exe'
    :param remove_flag: 是否删除原文件，默认为 True
    """
    # 转换为 normal 路径
    input_path = path.normpath(input_path)
    # 读取文件列表
    music_files = listdir(input_path)
    music_files = [(file, MP3(input_path + sep + file).info.length) for file in music_files if file.endswith('.mp3')]
    clip_need, rename_need = _re_name(music_files)  # 读取需要切片和需要重命名的文件列表
    count = 1 + len(clip_need)
    # 更新进度条
    update_progress(process_inner_list, 1, count, input_path, input_path)
    # 重命名文件（耗时极少，将其视为 1 个 事件）
    for old_name, new_name in rename_need:
        try:
            copy(input_path + sep + old_name, output_path + sep + new_name)
            logger.info(f'重命名文件：{old_name} -> {new_name}')
            if remove_flag:
                remove(input_path + sep + old_name)
                logger.info(f'删除旧文件：{old_name}')
        except FileExistsError:
            logger.warning(f'文件已存在：{new_name}')
    # 如果有需要切片的文件
    if clip_need:
        for i, (old_name, new_name, sta, end) in enumerate(clip_need):  # 解包需切片文件列表：旧文件名，新文件名，切片起始时间，切片结束时间
            # 设置新旧文件完整路径
            old = input_path + sep + old_name
            new = output_path + sep + new_name
            # 更新进度条
            update_progress(process_inner_list, i + 2, count, old_name, new_name)
            try:
                # 利用 subprocess.run 调用 ffmpeg.exe 进行音乐切片处理(单位:s)，不调用命令行
                # '-vn -acodec copy' 可以使用原音乐编码，否则编码不同会导致表现出的长度不同
                result = run(f'"{ffmpeg_path}" -i "{old}" -vn -acodec copy -ss {sta} -to {end} "{new}" -y',
                             capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW)
                if result.returncode == 0:
                    logger.info(f'切片文件：{old} -> {new}')
                    if remove_flag:
                        remove(old)
                        logger.info(f'删除旧文件：{old}')
                else:
                    logger.error(f'切片失败：{old} -> {new}， {result.stderr}')
            except FileNotFoundError:
                logger.error(f'切片失败：ffmpeg.exe 未找到')
                break
    else:  # 如果没有需要切片的文件
        logger.info('无需切片')


def mp3_gain(input_path: str, db: int, logger: logging.Logger, process_inner_list: list,
             mp3gain_path: str = 'mp3gain.exe'):
    """
    调用 mp3gain.exe 程序将输入 mp3 音乐文件的音量调整到相应的分贝数

    :param input_path: 输入文件夹（需要调整音量的音乐文件所在的路径）
    :param db: 音乐文件准备调整到的分贝数
    :param logger: 日志记录器
    :param process_inner_list: 进度条控件列表
    :param mp3gain_path: mp3gain.exe 文件的路径，默认为 'mp3gain.exe'
    """
    # 转换为 normal 路径
    input_path = path.normpath(input_path)
    # 读取音乐文件列表
    music_files = listdir(input_path)
    count = len(music_files)
    if music_files:  # 如果音乐文件列表不为空
        for i, music in enumerate(music_files):
            # 更新进度条
            update_progress(process_inner_list, i + 1, count, music, music)
            try:
                # 利用 subprocess.Popen 调用 mp3gain.exe 进行音量调整，不调用命令行
                # /d 意为调整分贝数，为相对于 89dB 的相对分贝数； /c 代表无需确认； /r 后跟需要进行操作的文件
                result = run(f'"{mp3gain_path}" /d {db - 89} /c /r "{input_path}\\{music}"',
                             capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
                if result.returncode == 0:
                    logger.info(f'调整音量：{music} -> {db}dB')
                else:
                    logger.error(f'调整音量失败：{music} -> {db}dB， {result.stderr}')
            except FileNotFoundError:
                logger.error(f'调整音量失败：mp3gain.exe 未找到')
                break
    else:  # 如果音乐文件列表为空
        logger.warning(f'音乐文件夹 {input_path} 为空')


if __name__ == '__main__':
    print('mp3_operations')
