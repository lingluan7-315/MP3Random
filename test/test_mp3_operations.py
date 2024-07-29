# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# 凌乱之主
# 2024年07月26日
import os
from subprocess import CREATE_NO_WINDOW
from unittest.mock import patch, MagicMock

import pytest
from MP3Random.mp3random.mp3_operations import backup, to_mp3, mp3_clip, mp3_gain, _re_name


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def paths(tmp_path):
    old_path = tmp_path / "old"
    music_path = tmp_path / "music"
    backup_path = tmp_path / "backup"
    os.makedirs(old_path)
    os.makedirs(music_path)
    os.makedirs(backup_path)
    return old_path, music_path, backup_path


@pytest.fixture
def create_old_file(paths):
    old_path, music_path, backup_path = paths
    old_file = old_path / "test.wav"
    old_file.touch()
    return old_file


@pytest.fixture
def create_music_file(paths):
    old_path, music_path, backup_path = paths
    old_file = music_path / "test(30.5-45).mp3"
    old_file.touch()
    return old_file


@pytest.fixture
def create_music_gain_file(paths):
    old_path, music_path, backup_path = paths
    music_file = music_path / "test.mp3"
    music_file.touch()
    return music_file


@patch('MP3Random.mp3random.mp3_operations.copytree')
@patch('MP3Random.mp3random.mp3_operations.rmtree')
@patch('MP3Random.mp3random.mp3_operations.path.exists')
def test_backup(mock_exists, mock_rmtree, mock_copytree, mock_logger):
    """测试 - 备份文件夹"""
    mock_exists.return_value = True
    result = backup('/source', '/backup', mock_logger)
    expected_backup_place = os.path.normpath('/backup/source')
    mock_rmtree.assert_called_once_with(expected_backup_place)
    mock_copytree.assert_called_once_with('/source', expected_backup_place)
    mock_logger.info.assert_any_call(f'删除已存在的备份文件夹：{expected_backup_place}')
    mock_logger.info.assert_any_call(f'备份文件夹：/source -> {expected_backup_place}')
    assert result

    mock_exists.return_value = False
    mock_rmtree.reset_mock()
    mock_copytree.reset_mock()
    result = backup('/source', '/backup', mock_logger)
    mock_rmtree.assert_not_called()
    mock_copytree.assert_called_with('/source', expected_backup_place)
    mock_logger.info.assert_any_call(f'备份文件夹：/source -> {expected_backup_place}')
    assert result


@patch('MP3Random.mp3random.mp3_operations.copytree')
@patch('MP3Random.mp3random.mp3_operations.rmtree')
@patch('MP3Random.mp3random.mp3_operations.path.exists')
def test_backup_no_write_permission(mock_exists, mock_rmtree, mock_copytree, mock_logger):
    """测试 - 备份文件夹 - 无写入权限"""
    mock_exists.return_value = True
    mock_copytree.side_effect = PermissionError("No write permission")
    result = backup('/source', '/backup', mock_logger)
    mock_rmtree.assert_called_once()
    mock_logger.error.assert_called_once_with('备份文件夹 /source 失败：No write permission')
    assert not result


@patch('MP3Random.mp3random.mp3_operations.copytree')
@patch('MP3Random.mp3random.mp3_operations.rmtree')
@patch('MP3Random.mp3random.mp3_operations.path.exists')
def test_backup_source_not_exist(mock_exists, mock_rmtree, mock_copytree, mock_logger):
    """测试 - 备份文件夹 - 源文件夹不存在"""
    mock_exists.return_value = False
    mock_copytree.side_effect = FileNotFoundError("No such file or directory")
    result = backup('/nonexistent_source', '/backup', mock_logger)
    expected_backup_place = os.path.normpath('/backup/nonexistent_source')
    mock_rmtree.assert_not_called()
    mock_copytree.assert_called_once_with('/nonexistent_source', expected_backup_place)
    mock_logger.error.assert_called_once_with('备份文件夹 /nonexistent_source 失败：No such file or directory')
    assert not result


@patch('MP3Random.mp3random.mp3_operations.copytree')
@patch('MP3Random.mp3random.mp3_operations.rmtree')
@patch('MP3Random.mp3random.mp3_operations.path.exists')
def test_backup_io_error(mock_exists, mock_rmtree, mock_copytree, mock_logger):
    """测试 - 备份文件夹 - I/O 错误"""
    mock_exists.return_value = True
    mock_copytree.side_effect = IOError("I/O error")
    result = backup('/source', '/backup', mock_logger)
    mock_rmtree.assert_called_once()
    mock_logger.error.assert_called_once_with('备份文件夹 /source 失败：I/O error')
    assert not result


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test.wav'])
@patch('MP3Random.mp3random.mp3_operations.run')
@patch('MP3Random.mp3random.mp3_operations.remove')
def test_to_mp3(mock_remove, mock_run, mock_listdir, mock_logger, paths, create_old_file):
    """测试 - 转换为 MP3"""
    old_path, music_path, backup_path = paths
    old_file = create_old_file
    mock_run.return_value.returncode = 0

    to_mp3(str(old_path), str(music_path), mock_logger)

    mock_run.assert_called_once_with(
        f'"ffmpeg.exe" -i "{old_file}" -b:a 128k "{music_path}\\test.mp3" -y',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_remove.assert_called_once_with(os.path.normpath(old_file))
    mock_logger.info.assert_any_call(f'转换文件：{old_file} -> {music_path}\\test.mp3')
    mock_logger.info.assert_any_call(f'删除旧文件：{old_file}')


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=[])
def test_to_mp3_no_files(mock_listdir, mock_logger, paths):
    """测试 - 转换为 MP3 - 无文件"""
    old_path, music_path, backup_path = paths
    to_mp3(str(old_path), str(music_path), mock_logger)
    mock_logger.warning.assert_called_once_with(f'音乐文件夹 {old_path} 为空')


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test.wav'])
@patch('MP3Random.mp3random.mp3_operations.run', side_effect=FileNotFoundError)
def test_to_mp3_ffmpeg_not_found(mock_run, mock_listdir, mock_logger, paths, create_old_file):
    """测试 - 转换为 MP3 - ffmpeg.exe 未找到"""
    old_path, music_path, backup_path = paths
    old_file = create_old_file

    to_mp3(str(old_path), str(music_path), mock_logger)

    mock_run.assert_called_once_with(
        f'"ffmpeg.exe" -i "{old_file}" -b:a 128k "{music_path}\\test.mp3" -y',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.error.assert_called_once_with(
        f'转换失败：ffmpeg.exe 未找到'
    )


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test.wav'])
@patch('MP3Random.mp3random.mp3_operations.run')
@patch('MP3Random.mp3random.mp3_operations.remove')
def test_to_mp3_ffmpeg_path_no_remove(mock_remove, mock_run, mock_listdir, mock_logger, paths, create_old_file):
    """测试 - 转换为 MP3 - 不删除原文件"""
    old_path, music_path, backup_path = paths
    old_file = create_old_file
    mock_run.return_value.returncode = 0
    ffmpeg_path = 'adcf 5/ffmpeg_15sd1_ds.exe'

    to_mp3(str(old_path), str(music_path), mock_logger, ffmpeg_path, False)

    mock_run.assert_called_once_with(
        f'"{ffmpeg_path}" -i "{old_file}" -b:a 128k "{music_path}\\test.mp3" -y',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.info.assert_any_call(f'转换文件：{old_file} -> {music_path}\\test.mp3')
    mock_remove.assert_not_called()


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test.wav'])
@patch('MP3Random.mp3random.mp3_operations.run', return_value=MagicMock(returncode=1, stderr="Error"))
def test_to_mp3_conversion_fail(mock_run, mock_listdir, mock_logger, paths, create_old_file):
    """测试 - 转换为 MP3 - 转换失败"""
    old_path, music_path, backup_path = paths
    old_file = create_old_file

    to_mp3(str(old_path), str(music_path), mock_logger)

    mock_run.assert_called_once_with(
        f'"ffmpeg.exe" -i "{old_file}" -b:a 128k "{music_path}\\test.mp3" -y',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.error.assert_called_once_with(
        f'转换失败：{old_file} -> {music_path}\\test.mp3， Error'
    )


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test(30.5-45).mp3'])
@patch('MP3Random.mp3random.mp3_operations.MP3')
@patch('MP3Random.mp3random.mp3_operations.copy')
@patch('MP3Random.mp3random.mp3_operations.run')
@patch('MP3Random.mp3random.mp3_operations.remove')
def test_mp3_clip(mock_remove, mock_run, mock_copy, mock_mp3, mock_listdir, mock_logger, paths, create_music_file):
    """测试 - 切片 MP3"""
    music_path = paths[1]
    old_file = os.path.normpath(create_music_file)
    mock_mp3.return_value.info.length = 60
    mock_run.return_value.returncode = 0

    mp3_clip(str(music_path), str(music_path), mock_logger)

    mock_copy.assert_not_called()
    mock_run.assert_called_once_with(
        f'"ffmpeg.exe" -i "{old_file}" -vn -acodec copy -ss 30.5 -to 45.0 "{music_path / "test.mp3"}" -y',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_remove.assert_called_once_with(old_file)
    mock_logger.info.assert_any_call(f'切片文件：{old_file} -> {music_path / "test.mp3"}')


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test(---).mp3'])
@patch('MP3Random.mp3random.mp3_operations.MP3')
@patch('MP3Random.mp3random.mp3_operations.copy')
@patch('MP3Random.mp3random.mp3_operations.remove')
def test_mp3_clip_rename(mock_remove, mock_copy, mock_mp3, mock_listdir, mock_logger, paths, create_music_file):
    """测试 - 切片 MP3 - 重命名"""
    music_path = paths[1]
    old_file = os.path.normpath(create_music_file)
    mock_mp3.return_value.info.length = 20

    mp3_clip(str(music_path), str(music_path), mock_logger)

    print(mock_logger.info.call_args_list)
    mock_copy.assert_called_once_with(old_file, music_path / "test.mp3")
    mock_remove.assert_called_once_with(old_file)
    mock_logger.info.assert_any_call(f'重命名文件：{old_file} -> {music_path / "test.mp3"}')


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test(30.5-45).mp3'])
@patch('MP3Random.mp3random.mp3_operations.MP3')
def test_mp3_clip_rename(mock_mp3, mock_listdir, mock_logger, paths, create_music_file):
    """测试 - 切片 MP3 - 无需切片"""
    music_path = paths[1]
    mock_mp3.return_value.info.length = 20

    mp3_clip(str(music_path), str(music_path), mock_logger)

    mock_logger.info.assert_any_call(f'无需切片')


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test(30.5-45).mp3'])
@patch('MP3Random.mp3random.mp3_operations.MP3')
@patch('MP3Random.mp3random.mp3_operations.copy')
@patch('MP3Random.mp3random.mp3_operations.run')
@patch('MP3Random.mp3random.mp3_operations.remove')
def test_mp3_clip_ffmpeg_path_no_remove(mock_remove, mock_run, mock_copy, mock_mp3, mock_listdir, mock_logger, paths,
                                        create_music_file):
    """测试 - 切片 MP3 - 不删除原文件"""
    music_path = paths[1]
    old_file = os.path.normpath(create_music_file)
    mock_mp3.return_value.info.length = 60
    mock_run.return_value.returncode = 0
    ffmpeg_path = 'adcf 5/ffmpeg_15sd1_ds.exe'

    mp3_clip(str(music_path), str(music_path), mock_logger, ffmpeg_path, False)

    mock_copy.assert_not_called()
    mock_run.assert_called_once_with(
        f'"{ffmpeg_path}" -i "{old_file}" -vn -acodec copy -ss 30.5 -to 45.0 "{music_path / "test.mp3"}" -y',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_remove.assert_not_called()
    mock_logger.info.assert_any_call(f'切片文件：{old_file} -> {music_path / "test.mp3"}')


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test(30.5-45).mp3'])
@patch('MP3Random.mp3random.mp3_operations.MP3')
@patch('MP3Random.mp3random.mp3_operations.run')
def test_mp3_clip_error(mock_run, mock_mp3, mock_listdir, mock_logger, paths, create_music_file):
    """测试 - 切片 MP3 - 错误"""
    music_path = paths[1]
    old_file = os.path.normpath(create_music_file)
    mock_mp3.return_value.info.length = 60
    mock_run.return_value.returncode = 4294967274
    mock_run.return_value.stderr = "Error: Invalid argument"

    mp3_clip(str(music_path), str(music_path), mock_logger)

    mock_run.assert_called_once_with(
        f'"ffmpeg.exe" -i "{old_file}" -vn -acodec copy -ss 30.5 -to 45.0 "{music_path / "test.mp3"}" -y',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.error.assert_called_once_with(
        f'切片失败：{old_file} -> {music_path / "test.mp3"}， Error: Invalid argument')


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test(30.5-45).mp3'])
@patch('MP3Random.mp3random.mp3_operations.MP3')
@patch('MP3Random.mp3random.mp3_operations.run', side_effect=FileNotFoundError)
def test_mp3_clip_ffmpeg_not_found(mock_run, mock_mp3, mock_listdir, mock_logger, paths, create_music_file):
    """测试 - 切片 MP3 - ffmpeg.exe 未找到"""
    music_path = paths[1]
    old_file = create_music_file
    mock_mp3.return_value.info.length = 60

    mp3_clip(str(music_path), str(music_path), mock_logger)

    mock_run.assert_called_once_with(
        f'"ffmpeg.exe" -i "{old_file}" -vn -acodec copy -ss 30.5 -to 45.0 "{music_path / "test.mp3"}" -y',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.error.assert_called_once_with(
        f'切片失败：ffmpeg.exe 未找到'
    )


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test(30.5-45).mp3'])
@patch('MP3Random.mp3random.mp3_operations.MP3')
@patch('MP3Random.mp3random.mp3_operations.run', return_value=MagicMock(returncode=1, stderr="Error"))
def test_mp3_clip_conversion_fail(mock_run, mock_mp3, mock_listdir, mock_logger, paths, create_music_file):
    """测试 - 切片 MP3 - 切片失败"""
    music_path = paths[1]
    old_file = create_music_file
    mock_mp3.return_value.info.length = 60

    mp3_clip(str(music_path), str(music_path), mock_logger)

    mock_run.assert_called_once_with(
        f'"ffmpeg.exe" -i "{old_file}" -vn -acodec copy -ss 30.5 -to 45.0 "{music_path / "test.mp3"}" -y',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.error.assert_called_once_with(
        f'切片失败：{old_file} -> {music_path / "test.mp3"}， Error'
    )


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test.mp3'])
@patch('MP3Random.mp3random.mp3_operations.run')
def test_mp3_gain(mock_run, mock_listdir, mock_logger, paths, create_music_gain_file):
    """测试 - 调整音量"""
    music_path, backup_path = paths[1], paths[2]
    music_file = os.path.normpath(create_music_gain_file)
    mock_run.return_value.returncode = 0

    mp3_gain(str(music_path), 95, mock_logger)

    mock_run.assert_called_once_with(
        f'"mp3gain.exe" /d 6 /c /r "{music_file}"',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.info.assert_any_call(f'调整音量：test.mp3 -> 95dB')


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test.mp3'])
@patch('MP3Random.mp3random.mp3_operations.run')
def test_mp3_gain_mp3gain_path(mock_run, mock_listdir, mock_logger, paths, create_music_gain_file):
    """测试 - 调整音量 - mp3gain_path"""
    music_path, backup_path = paths[1], paths[2]
    music_file = os.path.normpath(create_music_gain_file)
    mock_run.return_value.returncode = 0
    mp3gain_path = 'adcf 5/mp3gain_15sd1_ds.exe'

    mp3_gain(str(music_path), 95, mock_logger, mp3gain_path)

    mock_run.assert_called_once_with(
        f'"{mp3gain_path}" /d 6 /c /r "{music_file}"',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.info.assert_any_call(f'调整音量：test.mp3 -> 95dB')


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test.mp3'])
@patch('MP3Random.mp3random.mp3_operations.run', side_effect=FileNotFoundError)
def test_mp3_gain_mp3gain_not_found(mock_run, mock_listdir, mock_logger, paths, create_music_gain_file):
    """测试 - 调整音量 - mp3gain.exe 未找到"""
    music_path, backup_path = paths[1], paths[2]
    music_file = create_music_gain_file

    mp3_gain(str(music_path), 95, mock_logger)

    mock_run.assert_called_once_with(
        f'"mp3gain.exe" /d 6 /c /r "{music_file}"',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.error.assert_called_once_with(
        f'调整音量失败：mp3gain.exe 未找到'
    )


@patch('MP3Random.mp3random.mp3_operations.listdir', return_value=['test.mp3'])
@patch('MP3Random.mp3random.mp3_operations.run', return_value=MagicMock(returncode=1, stderr="Error"))
def test_mp3_gain_fail(mock_run, mock_listdir, mock_logger, paths, create_music_gain_file):
    """测试 - 调整音量 - 失败"""
    music_path, backup_path = paths[1], paths[2]
    music_file = create_music_gain_file

    mp3_gain(str(music_path), 95, mock_logger)

    mock_run.assert_called_once_with(
        f'"mp3gain.exe" /d 6 /c /r "{music_file}"',
        capture_output=True, text=True, encoding='utf-8', creationflags=CREATE_NO_WINDOW
    )
    mock_logger.error.assert_called_once_with(
        f'调整音量失败：{os.path.basename(music_file)} -> 95dB， Error'
    )


@pytest.mark.parametrize("files, expected_clip, expected_rename", [
    ([("song（30.5-10.0).mp3", 60.0)], [["song（30.5-10.0).mp3", "song.mp3", 10.0, 30.5]], []),
    ([("song.mp3", 60.0)], [], []),  # no need to clip or rename
    ([("song(--.mp3", 60.0)], [], []),
    ([("song--).mp3", 60.0)], [], []),
    ([("song(---).mp3", 60.0)], [], [["song(---).mp3", "song.mp3"]]),  # no need to clip, but need to rename
    ([("song(----).mp3", 60.0)], [], []),
    ([("song(-30.5-).mp3", 60.0)], [["song(-30.5-).mp3", "song.mp3", 29.5, 60.0]], []),
    ([("song(--10.0).mp3", 60.0)], [["song(--10.0).mp3", "song.mp3", 0.0, 50.0]], []),
    ([("song（-30.5-10.0）.mp3", 60.0), ("other.mp3", 60.0)], [["song（-30.5-10.0）.mp3", "song.mp3", 10.0, 29.5]], []),
    ([(".mp3", 60.0)], [], []),  # file name is empty
    ([("(5--10）.mp3", 60.0)], [["(5--10）.mp3", "_2.mp3", 5.0, 50.0]], []),  # file name is not valid
    ([("song(5--6).m4s", 60.0), ("song(5-6).mp3", 60.0)],
     [["song(5--6).m4s", "song.mp3", 5.0, 54.0], ["song(5-6).mp3", "song_2.mp3", 5.0, 6.0]], []),
    ([], [], []),  # no files
    ([("song(100--5).mp3", 60.0)], [["song(100--5).mp3", "song.mp3", 55.0, 60.0]], []),
    ([("song(100-200).mp3", 60.0)], [], []),
    ([("song(100-200)", 60.0)], [], []),  # no extension
    ([("song(-30.5--10).mp3", 60.0)] * 100,
     [["song(-30.5--10).mp3", f"song{'_2' * i}.mp3", 29.5, 50.0] for i in range(100)], []),
    ([(f"song({i}-{i + 1}).mp3", 60.0) for i in range(100)],
     [[f"song({i}-{i + 1}).mp3", f"song{'_2' * i}.mp3", i, i + 1] for i in range(60)], []),
])
def test_re_name(files, expected_clip, expected_rename):
    """测试 - 切片和重命名文件名称提取"""
    clip_need, rename_need = _re_name(files)
    assert clip_need == expected_clip
    assert rename_need == expected_rename
