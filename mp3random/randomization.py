#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 凌乱之主
# 2024年07月25日
"""
随机排列音乐文件

- mp3_random: 进行随机排列，并将结果保存至文件夹，生成结果统计txt文件
"""
import logging
from os import path, sep, listdir, remove
from random import shuffle
from re import match, compile
from shutil import copy, rmtree

from mutagen.mp3 import MP3

from utils import create_path, time_list_from


def _get_random(music_files: list[str]) -> (list[str], int, float):
    """
    随机排列音乐文件

    :param music_files: 音乐文件列表
    :return: 随机排列的结果，包括文件名列表、最小相邻次数、随机质量
    """
    count = len(music_files)
    if count == 0:
        return [], 0, 0.0

    min_adjacent_count = float('inf')  # 初始化为无穷大
    best_result = []
    best_quality = 0.0
    # 获取文件标签
    label = compile('[\[【［](.*)[]】］].*')
    labels_dict = {name: label.match(name).group(1) if label.match(name) else '无标签' for name in music_files}
    # 将文件按标签排序
    sorted_files = sorted(music_files, key=lambda x: labels_dict[x])
    max_num_range = int(count * 0.7)
    # 遍历每个可能的分组大小
    for max_num in range(1, max_num_range + 1):
        # 按照最大允许数量分组
        groups = [sorted_files[i: i + max_num] for i in range(0, count, max_num)]

        # 循环100次寻找当前分组大小下的最优结果
        for _ in range(100):
            # 随机排列组内文件及组间分组
            [shuffle(group) for group in groups]
            shuffle(groups)

            # 交叉合并分组
            interleaved = []
            i = 0
            j = len(groups) - 1
            while i <= j:
                # 若 i == j ，则该组为单组，可将其随机插入到结果中
                if i == j:
                    interleaved.extend(groups[i])
                else:  # 否则将两组交叉插入到结果中
                    for k in range(max_num):
                        if k < len(groups[i]):
                            interleaved.append(groups[i][k])
                        if k < len(groups[j]):
                            interleaved.append(groups[j][k])
                i += 1
                j -= 1

            # 计算标签和相邻次数
            interleaved_labels = [labels_dict[name] for name in interleaved]
            adjacent_count = sum(a == b for a, b in zip(interleaved_labels[1:], interleaved_labels[:-1]))

            # 更新最优结果（查找最小相邻次数和最大分组大小）
            if adjacent_count <= min_adjacent_count:
                min_adjacent_count = adjacent_count
                best_result = interleaved
                best_quality = max_num / max_num_range * 100

    return best_result, min_adjacent_count, best_quality


def mp3_random(input_path: str, output_path: str, result_txt: str, logger: logging.Logger,
               label_flag: bool = False, name_flag: bool = False, remove_flag: bool = False):
    """
    进行随机排列，并将结果保存至文件夹，生成结果统计txt文件

    :param input_path: 输入文件夹（音乐文件所在的路径）
    :param output_path: 输出文件夹（随机排列后的音乐文件保存路径）
    :param result_txt: 结果统计txt文件
    :param logger: 日志对象
    :param label_flag: 是否将标签添加到随机后文件名，若标签和原文件名都添加，则标签在前
    :param name_flag: 是否将原文件名添加到随机后文件名，若标签和原文件名都添加，则标签在前
    :param remove_flag: 是否删除原文件夹，默认为False
    """
    logger.info('开始随机排列')
    # 读取音乐文件列表
    try:
        music_files = listdir(input_path)
    except FileNotFoundError:
        logger.error(f'音乐文件夹 {input_path} 未找到')
        return
    count = len(music_files)
    if music_files:  # 如果文件列表不为空
        # 如果随机文件保存目录存在则删除该目录
        if path.exists(output_path):
            rmtree(output_path)
            logger.info(f'删除已存在的随机文件保存目录：{output_path}')
        # 重新创建随机文件保存目录
        create_path(output_path)
        # 进行随机排列
        random_result, random_same, random_quality = _get_random(music_files)
        # 创建符合文件数量的相应数字符串型列表
        new_ids = ["{:0{}d}".format(i, len(str(count))) for i in range(1, count + 1)]

        # 获取原文件标签进行分类统计
        labels = [match('[\[【［](.*)[]】］].*', name).group(1)
                  if match('[\[【［](.*)[]】］].*', name) else '无标签' for name in music_files]
        labels_dict = {name: label for name, label in zip(music_files, labels)}
        names = [match('.*[\[【［].*[]】］](.*)', name).group(1)
                 if match('.*[\[【［].*[]】］](.*)', name) else name for name in music_files]
        names_dict = {name: path.splitext(n)[0] for name, n in zip(music_files, names)}
        # 获取每个标签的文件位置索引
        labels_index = {ll: [i for i, l in enumerate(labels) if l == ll] for ll in set(labels)}
        # 对每个标签进行计数，并按照数量降序排列
        labels_num = {ll: len(l) for ll, l in labels_index.items()}
        labels_num = sorted(zip(labels_num.values(), labels_num.keys()), reverse=True)
        # 获取原文件的时间列表
        time_list = [MP3(input_path + sep + file).info.length for file in music_files]
        # 获取分组时间列表，并将其格式化为总时长、平均时长
        time_group = {ll: time_list_from([time_list[t] for t in i]) for ll, i in labels_index.items()}
        # 计算全部文件的总时长和平均时长
        time_all = time_list_from(time_list)
        # 将分类统计结果和排序结果放在txt文件中
        with open(result_txt, 'w') as txt:
            txt.write('【分类统计】\n标签：个数 - 总时长 - 平均时长\n')
            txt.write('总计：{} - {} - {}\n'.format(len(music_files), time_all[0], time_all[1]))
            for num, key in labels_num:
                txt.write('{}：{} - {} - {}\n'.format(key, num, time_group[key][0], time_group[key][1]))
            txt.write('【排序结果】\n')
            txt.write('  相邻次数：{}\n'.format(random_same))
            txt.write('  随机质量：{:.1f}%\n'.format(random_quality))
            for i in range(len(random_result)):
                txt.write(new_ids[i] + ' ' + random_result[i] + '\n')
        logger.info(f'生成结果统计文件：{result_txt}')

        # 遍历新旧文件名称列表，进行随机排列
        for old_name, new_id in zip(random_result, new_ids):
            old_file_name = input_path + sep + old_name
            # 获取新文件名
            new_file_name = output_path + sep + new_id
            if label_flag:
                new_file_name += f'[{labels_dict[old_name]}]'
            if name_flag:
                new_file_name += f'{names_dict[old_name]}'
            new_file_name += '.mp3'
            copy(old_file_name, new_file_name)
            logger.info(f'随机排列：{old_file_name} -> {new_file_name}')
            if remove_flag:
                remove(old_file_name)
                logger.info(f'删除旧文件：{old_file_name}')

        logger.info('随机排列完成')
    else:  # 如果文件列表为空
        time_zero = time_list_from([])
        with open(result_txt, 'w') as txt:
            txt.write('【分类统计】\n标签：个数 - 总时长 - 平均时长\n')
            txt.write('总计：{} - {} - {}\n'.format(0, time_zero[0], time_zero[1]))
            txt.write('【排序结果】\n  相邻次数：-\n  随机质量：-%\n')
        logger.warning('音乐文件夹为空，未进行随机排列')


if __name__ == '__main__':
    print('randomization')
