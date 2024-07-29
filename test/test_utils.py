# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# 凌乱之主
# 2024年07月26日
import logging
import os
from unittest.mock import patch

import pytest
from MP3Random.mp3random.utils import create_logger, create_path, time_from, time_list_from, check_dependence


def test_create_logger():
    """测试 - 创建 logger"""
    logger = create_logger('TestLogger', 'test.log', logging.INFO)
    assert logger.name == 'TestLogger'
    assert len(logger.handlers) == 2
    assert logger.level == logging.INFO
    # 关闭并移除所有 handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    os.remove('test.log')


@pytest.mark.parametrize("log_level", [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL])
def test_create_logger_levels(log_level):
    """测试 - 创建 logger 不同等级"""
    logger = create_logger('TestLogger', 'test.log', log_level)
    assert logger.level == log_level
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    os.remove('test.log')


def test_create_path(tmp_path):
    """测试 - 创建文件夹"""
    test_dir = tmp_path / "new_directory"
    created_path = create_path(str(test_dir))
    assert os.path.exists(created_path)
    assert created_path == str(test_dir)


def test_create_path_existing(tmp_path):
    """测试 - 创建已存在的文件夹"""
    test_dir = tmp_path / "existing_directory"
    os.makedirs(test_dir)
    created_path = create_path(str(test_dir))
    assert os.path.exists(created_path)
    assert created_path == str(test_dir)


def test_create_path_multilevel(tmp_path):
    """测试 - 创建多级文件夹"""
    test_dir = tmp_path / "new_directory/level1/level2"
    created_path = create_path(str(test_dir))
    assert os.path.exists(created_path)
    assert created_path == str(test_dir)


def test_create_path_special_characters(tmp_path):
    """测试 - 创建包含特殊字符的文件夹"""
    test_dir = tmp_path / "new_directory/@!#%&()"
    created_path = create_path(str(test_dir))
    assert os.path.exists(created_path)
    assert created_path == str(test_dir)


@pytest.mark.parametrize("seconds, expected", [
    (3661, '01h01m01s'),
    (0, '00h00m00s'),
    (86400, '24h00m00s'),
    (31536000, '8760h00m00s'),  # One year in seconds
    (-10, '00h00m00s'),  # Negative seconds
    (0.5, '00h00m00s'),  # Less than one second
])
def test_time_from(seconds, expected):
    """测试 - 格式化时间秒数为“0h0m0s”格式"""
    assert time_from(seconds) == expected


@pytest.mark.parametrize("time_list, expected_total, expected_avg", [
    ([3600, 1800, 7200], '03:30:00', '70:00'),
    ([], '00:00:00', '00:00'),
    ([60], '00:01:00', '01:00'),
    ([i for i in range(10, 1000, 10)], '13:45:00', '08:20'),
    ([36, 18, 72], '00:02:06', '00:42'),
    ([86400, 43200, 172800], '84:00:00', '1680:00'),
    ([31536000], '8760:00:00', '525600:00'),  # One year in seconds
    ([3600.5, 1800.5, 7200.5], '03:30:02', '70:00'),  # Decimal seconds
    ([-60, -120, -180], '00:00:00', '00:00'),  # Negative seconds
    ([1] * 1000000, '277:46:40', '00:01'),  # Very large list
])
def test_time_list_from(time_list, expected_total, expected_avg):
    """测试 - 格式化时间列表为“-h-m-s”和“-m-s”格式"""
    assert time_list_from(time_list) == (expected_total, expected_avg)


@patch('MP3Random.mp3random.utils.path.exists')
def test_check_dependence_current_folder(mocked_exists):
    """测试 - 检查依赖是否存在 - 当前文件夹"""
    mocked_exists.return_value = True
    assert check_dependence('ffmpeg.exe') is True
    mocked_exists.assert_called_once_with('ffmpeg.exe')


@patch('MP3Random.mp3random.utils.path.exists')
@patch('MP3Random.mp3random.utils.path.dirname')
def test_check_dependence_env_folder(mocked_dirname, mocked_exists):
    """测试 - 检查依赖是否存在 - 环境变量文件夹"""
    mocked_exists.side_effect = [False, True]
    mocked_dirname.return_value = '/mocked/path'
    assert check_dependence('ffmpeg.exe') is True
    mocked_exists.assert_any_call('ffmpeg.exe')
    mocked_exists.assert_any_call(os.path.join('/mocked/path', 'ffmpeg.exe'))


@patch('MP3Random.mp3random.utils.path.exists')
def test_check_dependence_not_found(mocked_exists):
    """测试 - 检查依赖是否存在 - 依赖不存在"""
    mocked_exists.return_value = False
    assert check_dependence('ffmpeg.exe') is False
