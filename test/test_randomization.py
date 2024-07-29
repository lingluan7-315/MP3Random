#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 凌乱之主
# 2024年07月25日
"""
测试：随机排列音乐文件（randomization.py）
"""
import os
import time
from unittest.mock import patch, mock_open, MagicMock

import pytest
from MP3Random.mp3random.randomization import _get_random, mp3_random

# 测试用例
test_cases = ['［标签4］测试8（---）.mp3',
              '【标签1】测试2(5.2--).mp3',
              '［标签4］测试10（-60）.mp3',
              '［标签1］测试3（--6）.mp3',
              '［标签3］测试6（他--8.2）.mp3',
              '【标签1］测试1(---5).mp3',
              '［标签4］测试11（--5）.mp3',
              '［标签2]测试4（0--10.5）.mp3',
              '［标签4】测试9（-50）.mp3',
              '测试12（8.2--6.8）.mp3',
              '[标签4]测试7（-40--2）.mp3',
              '[标签2］测试5（7-）.mp3']
random_cases = (test_cases, 0, 100.0)
labels_dict = {'［标签4］测试8（---）.mp3': '标签4',
               '【标签1】测试2(5.2--).mp3': '标签1',
               '［标签4］测试10（-60）.mp3': '标签4',
               '［标签1］测试3（--6）.mp3': '标签1',
               '［标签3］测试6（他--8.2）.mp3': '标签3',
               '【标签1］测试1(---5).mp3': '标签1',
               '［标签4］测试11（--5）.mp3': '标签4',
               '［标签2]测试4（0--10.5）.mp3': '标签2',
               '［标签4】测试9（-50）.mp3': '标签4',
               '测试12（8.2--6.8）.mp3': '无标签',
               '[标签4]测试7（-40--2）.mp3': '标签4',
               '[标签2］测试5（7-）.mp3': '标签2'}
names_dict = {'［标签4］测试8（---）.mp3': '测试8（---）',
              '【标签1】测试2(5.2--).mp3': '测试2(5.2--)',
              '［标签4］测试10（-60）.mp3': '测试10（-60）',
              '［标签1］测试3（--6）.mp3': '测试3（--6）',
              '［标签3］测试6（他--8.2）.mp3': '测试6（他--8.2）',
              '【标签1］测试1(---5).mp3': '测试1(---5)',
              '［标签4］测试11（--5）.mp3': '测试11（--5）',
              '［标签2]测试4（0--10.5）.mp3': '测试4（0--10.5）',
              '［标签4】测试9（-50）.mp3': '测试9（-50）',
              '测试12（8.2--6.8）.mp3': '测试12（8.2--6.8）',
              '[标签4]测试7（-40--2）.mp3': '测试7（-40--2）',
              '[标签2］测试5（7-）.mp3': '测试5（7-）'}


@pytest.fixture
def mock_mp3():
    with patch('MP3Random.mp3random.randomization.MP3') as mock:
        mock.return_value.info.length = 300.0
        yield mock


@pytest.fixture
def mock_open_file():
    with patch('MP3Random.mp3random.randomization.open', new_callable=mock_open) as mock:
        yield mock


@pytest.fixture
def mock_listdir():
    with patch('MP3Random.mp3random.randomization.listdir', return_value=test_cases) as mock:
        yield mock


@pytest.fixture
def mock_listdir_no_exist():
    with patch('MP3Random.mp3random.randomization.listdir', side_effect=FileNotFoundError) as mock:
        yield mock


@pytest.fixture
def mock_path_exists():
    with patch('MP3Random.mp3random.randomization.path.exists', side_effect=[False, True]) as mock:
        yield mock


@pytest.fixture
def mock_create_path():
    with patch('MP3Random.mp3random.randomization.create_path') as mock:
        yield mock


@pytest.fixture
def mock_get_random():
    with patch('MP3Random.mp3random.randomization._get_random', return_value=random_cases) as mock:
        yield mock


@pytest.fixture
def mock_copy():
    with patch('MP3Random.mp3random.randomization.copy') as mock:
        yield mock


@pytest.fixture
def mock_rmtree():
    with patch('MP3Random.mp3random.randomization.rmtree') as mock:
        yield mock


@pytest.fixture
def mock_logger():
    return MagicMock()


def test_get_random():
    """测试 - 获取随机结果（_get_random）"""
    result, min_adjacent_count, quality = _get_random(test_cases)
    assert isinstance(result, list)
    assert isinstance(min_adjacent_count, int)
    assert isinstance(quality, float)
    assert len(result) == len(test_cases)


def test_get_random_empty():
    """测试 - 获取随机结果（_get_random）- 空列表"""
    result, min_adjacent_count, quality = _get_random([])
    assert result == []
    assert min_adjacent_count == 0
    assert quality == 0.0


@pytest.mark.parametrize('num', [2, 5, 10, 20, 50, 100])
def test_get_random_performance(num):
    """测试 - 获取随机结果（_get_random）- 性能测试"""
    music_files = [f'[标签{j}]测试{i}.mp3' for i in range(num) for j in range(10)]
    start_time = time.perf_counter()
    result, min_adjacent_count, quality = _get_random(music_files)
    end_time = time.perf_counter()
    files_count = len(music_files)
    use_time = end_time - start_time

    print(f'\t[{files_count}]个文件随机排列结果质量：{quality:.2f}%，相邻次数：{min_adjacent_count}，耗时：{use_time:.4f}秒')
    assert isinstance(result, list)
    assert min_adjacent_count == 0  # 保证无相邻
    assert isinstance(quality, float)
    assert len(result) == len(music_files)
    assert use_time < 0.00005 * files_count * files_count + 0.0005 * files_count + 0.005


def test_mp3_random(
        mock_mp3,
        mock_open_file,
        mock_listdir,
        mock_path_exists,
        mock_create_path,
        mock_get_random,
        mock_copy,
        mock_rmtree,
        mock_logger
):
    """测试 - 随机排列音乐文件（mp3_random）"""
    music_path = 'test_music'
    random_path = 'test_random'
    result_txt = 'test_result.txt'
    mp3_random(music_path, random_path, result_txt, mock_logger)

    mock_create_path.assert_called_once_with(random_path)
    mock_get_random.assert_called_once()
    mock_open_file.assert_called_once_with(result_txt, 'w')
    mock_copy.assert_called()

    handle = mock_open_file()
    handle.write.assert_called()

    assert mock_mp3.call_count == 12

    for i, file in enumerate(test_cases):
        mock_copy.assert_any_call(
            os.path.join(music_path, file),
            os.path.join(random_path, f'{i + 1:02d}.mp3')
        )


@pytest.mark.parametrize('label_flag, name_flag', [(True, True), (True, False), (False, True), (False, False)])
def test_mp3_random_label_name(
        mock_mp3,
        mock_open_file,
        mock_listdir,
        mock_path_exists,
        mock_create_path,
        mock_get_random,
        mock_copy,
        mock_rmtree,
        mock_logger,
        label_flag,
        name_flag
):
    """测试 - 随机排列音乐文件（mp3_random） - 标签、名称标记"""
    music_path = 'test_music'
    random_path = 'test_random'
    result_txt = 'test_result.txt'
    mp3_random(music_path, random_path, result_txt, mock_logger, label_flag, name_flag)

    mock_create_path.assert_called_once_with(random_path)
    mock_get_random.assert_called_once()
    mock_open_file.assert_called_once_with(result_txt, 'w')
    mock_copy.assert_called()

    handle = mock_open_file()
    handle.write.assert_called()

    assert mock_mp3.call_count == 12

    for i, file in enumerate(test_cases):
        new_name = f'{i + 1:02d}'
        if label_flag:
            new_name += f'[{labels_dict[file]}]'
        if name_flag:
            new_name += f'{names_dict[file]}'
        mock_copy.assert_any_call(
            os.path.join(music_path, file),
            os.path.join(random_path, f'{new_name}.mp3')
        )


@patch('MP3Random.mp3random.randomization.remove')
def test_mp3_random_remove(
        mock_remove,
        mock_mp3,
        mock_open_file,
        mock_listdir,
        mock_path_exists,
        mock_create_path,
        mock_get_random,
        mock_copy,
        mock_rmtree,
        mock_logger
):
    """测试 - 随机排列音乐文件（mp3_random） - 删除原文件"""
    music_path = 'test_music'
    random_path = 'test_random'
    result_txt = 'test_result.txt'

    mp3_random(music_path, random_path, result_txt, mock_logger, remove_flag=True)

    mock_create_path.assert_called_once_with(random_path)
    mock_get_random.assert_called_once()
    mock_open_file.assert_called_once_with(result_txt, 'w')
    mock_copy.assert_called()

    handle = mock_open_file()
    handle.write.assert_called()

    assert mock_mp3.call_count == 12

    for i, file in enumerate(test_cases):
        mock_copy.assert_any_call(
            os.path.join(music_path, file),
            os.path.join(random_path, f'{i + 1:02d}.mp3')
        )
    mock_remove.assert_called()


def test_mp3_random_music_path_not_exist(
        mock_listdir_no_exist,
        mock_path_exists,
        mock_create_path,
        mock_get_random,
        mock_mp3,
        mock_open_file,
        mock_copy,
        mock_rmtree,
        mock_logger
):
    """测试 - 音乐文件夹不存在（mp3_random）"""
    music_path = 'nonexistent_music'
    random_path = 'test_random'
    result_txt = 'test_result.txt'

    mp3_random(music_path, random_path, result_txt, mock_logger)

    mock_logger.error.assert_called_once_with(f'音乐文件夹 {music_path} 未找到')


def test_mp3_random_result_txt_cannot_write(
        mock_mp3,
        mock_open_file,
        mock_listdir,
        mock_path_exists,
        mock_create_path,
        mock_get_random,
        mock_copy,
        mock_rmtree,
        mock_logger
):
    """测试 - 无法写入结果统计文件（mp3_random）"""
    mock_open_file.side_effect = IOError

    music_path = 'test_music'
    random_path = 'test_random'
    result_txt = 'cannot_write_result.txt'

    with pytest.raises(IOError):
        mp3_random(music_path, random_path, result_txt, mock_logger)

    mock_create_path.assert_called_once_with(random_path)
    mock_get_random.assert_called_once()
