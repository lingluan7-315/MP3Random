#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# 凌乱之主
# 2024年07月25日
import os
from os.path import normpath

import webview

from mp3_operations import backup, to_mp3, mp3_clip, mp3_gain
from randomization import mp3_random
from utils import create_logger, check_dependence, update_progress


def get_element(window, element_id):
    return window.dom.get_element('#' + element_id)


def value_replace(value):
    if value is None:
        return ''
    # 替换特殊字符（额外转义）
    if '\\' in value:
        value = value.replace('\\', '\\\\')
    return value


def check_dependence_flag(text_element, check_element):
    # 若依赖标志为真，则将文本设置为黑色，检查标志设置为✔️，并去除点击事件；否则，将文本设置为红色，检查标志设置为❌，并添加点击事件
    dependence_flag = check_dependence(text_element.text)
    if dependence_flag:
        text_element.attributes['class'] = 'normal'
        check_element.text = '✔️'
        check_element.attributes['class'] = 'normal'
    else:
        text_element.attributes['class'] = 'error'
        check_element.text = '❌'
        check_element.attributes['class'] = 'error'
    return dependence_flag


def get_dependence_file(window, text_element, check_element, directory, file_types):
    return_file = window.create_file_dialog(webview.OPEN_DIALOG, directory=directory, file_types=file_types)
    if return_file is not None:
        text_element.text = value_replace(return_file[0])
    check_dependence_flag(text_element, check_element)


def get_path(window, path_element, directory, path_types=None, file_types=None):
    if path_types is not None:
        return_path = window.create_file_dialog(webview.FOLDER_DIALOG, directory=directory)
        if return_path is not None:
            path_element.value = value_replace(return_path[0])
    elif file_types is not None:
        return_file = window.create_file_dialog(webview.OPEN_DIALOG, directory=directory, file_types=file_types)
        if return_file is not None:
            path_element.value = value_replace(return_file[0])
    else:
        raise ValueError('path_types and file_types cannot both be None')


def get_checked(window, checkbox_id_list):
    checked_dict = {}
    for checkbox_id in checkbox_id_list:
        checked_dict[checkbox_id] = window.evaluate_js(f'document.getElementById("{checkbox_id}").checked')
    return checked_dict


def start(window, input_element_list, checked_id_list, frame_size, dependence_list):
    # 获取所有的输入值（手动定义）
    ffmpeg, ffmpeg_check, mp3gain, mp3gain_check = dependence_list
    ffmpeg_path, mp3gain_path = (ffmpeg.text, mp3gain.text)
    old_path, music_path, db_select, random_path, result_txt, backup_path = [input_element.value for input_element in
                                                                             input_element_list]
    old_path_check, music_path_check, random_path_check, old_files_delete_check, music_files_delete_check, process_to_mp3_check, process_clip_mp3_check, process_mp3gain_check, process_random_check = [
        window.evaluate_js(f'document.getElementById("{checkbox_id}").checked') for checkbox_id in checked_id_list]
    # 根据可选项检查输入值
    error_message = ''
    # 检查依赖: [格式转换]、[音乐切片]使用ffmpeg，[音量调整]使用mp3gain，若未开启则不检查
    ffmpeg_flag = check_dependence_flag(ffmpeg, ffmpeg_check)
    mp3gain_flag = check_dependence_flag(mp3gain, mp3gain_check)
    if (process_to_mp3_check or process_clip_mp3_check) and not ffmpeg_flag:
        error_message += '未找到ffmpeg！\\n'
    if process_mp3gain_check and not mp3gain_flag:
        error_message += '未找到mp3gain！\\n'
    # 开启[格式转换]过程时
    if process_to_mp3_check:
        # [转换前音乐目录]不能为空，且必须存在，且不能与[转换后音乐目录]相同
        if old_path == '':
            error_message += '[转换前音乐目录]不能为空！\\n'
        if not os.path.exists(old_path):
            error_message += '[转换前音乐目录]不存在！\\n'
        if old_path == music_path:
            error_message += '[转换前音乐目录]不能与[转换后音乐目录]相同！\\n'
        # 若此条件下，再开启[音乐切片]或[音量调整]过程时
        if process_clip_mp3_check or process_mp3gain_check:
            pass
        else:
            pass
        # 若此条件下，再开启[随机排列]过程时
        if process_random_check:
            # [转换前音乐目录]不能与[随机排列后目录]相同，且[转换后音乐目录]也不能与[随机排列后目录]相同
            if old_path == random_path:
                error_message += '[转换前音乐目录]不能与[随机排列后目录]相同！\\n'
            if music_path == random_path:
                error_message += '[转换后音乐目录]不能与[随机排列后目录]相同！\\n'
        else:
            pass
    else:  # 未开启[格式转换]过程时
        # 若开启[音乐切片]或[音量调整]过程时
        if process_clip_mp3_check or process_mp3gain_check:
            # [转换后音乐目录]不能为空，且必须存在
            if music_path == '':
                error_message += '[转换后音乐目录]不能为空！\\n'
            if not os.path.exists(music_path):
                error_message += '[转换后音乐目录]不存在！\\n'
            # 若开启[随机排列]过程时
            if process_random_check:
                # [转换后音乐目录]不能与[随机排列后目录]相同
                if music_path == random_path:
                    error_message += '[转换后音乐目录]不能与[随机排列后目录]相同！\\n'
            else:
                pass
        else:  # 未开启[音乐切片]或[音量调整]过程时
            # 若开启[随机排列]过程时
            if process_random_check:
                # [转换后音乐目录]不能为空，且必须存在，且不能与[随机排列后目录]相同
                if music_path == '':
                    error_message += '[转换后音乐目录]不能为空！\\n'
                if not os.path.exists(music_path):
                    error_message += '[转换后音乐目录]不存在！\\n'
                if music_path == random_path:
                    error_message += '[转换后音乐目录]不能与[随机排列后目录]相同！\\n'
            else:
                # 任何过程都未开启时
                error_message += '请至少开启一个处理过程！\\n'
    # 处理备份检查
    # 当未开启[格式转换]过程时，old_path_check设置为False；
    # music_path_check 四个过程都可能用到，不进行修改
    # 当未开启[随机排列]过程时，random_path_check设置为False
    old_path_check = old_path_check and process_to_mp3_check
    random_path_check = random_path_check and process_random_check
    if (old_path_check or music_path_check or random_path_check) and backup_path == '':
        error_message += '[备份音乐文件至]不能为空！\\n'
    if old_path_check and old_path == backup_path:
        error_message += '[转换前音乐目录]不能与[备份音乐文件至]相同！\\n'
    if music_path_check and music_path == backup_path:
        error_message += '[转换后音乐目录]不能与[备份音乐文件至]相同！\\n'
    if random_path_check and random_path == backup_path:
        error_message += '[随机排列后目录]不能与[备份音乐文件至]相同！\\n'

    # 若有错误信息，则弹出提示框
    if error_message != '':
        window.evaluate_js(f'alert("{error_message}")')
        return
    # 若检查通过，则开始执行
    # 隐藏选项界面
    options = get_element(window, 'options')
    options.hide()
    # 显示运行界面
    process = get_element(window, 'process')
    process.show()
    # 调整窗口大小
    window.resize(650 + frame_size[0], 400 + frame_size[1])
    # 运行界面提示控件绑定
    process_name = get_element(window, 'process_name')
    progress = get_element(window, 'progress')
    progress_value = get_element(window, 'progress_value')
    process_old_file = get_element(window, 'process_old_file')
    process_new_file = get_element(window, 'process_new_file')
    process_inner_list = [progress, progress_value, process_old_file, process_new_file]
    # 计时处理
    window.evaluate_js("""StartTimer();""")

    # 开始运行 >>>
    # TODO: 日志记录嵌入界面
    logger = create_logger()
    logger.info('开始运行')
    # 转换为normal路径
    old_path = normpath(old_path)
    music_path = normpath(music_path)
    backup_path = normpath(backup_path)
    random_path = normpath(random_path)
    result_txt = normpath(result_txt)
    # 备份转换前音乐目录
    if old_path_check:
        process_name.text = '文件备份'
        update_progress(process_inner_list, 0, 1, old_path, backup_path)
        backup(old_path, backup_path, logger)
    # 转换为 MP3
    if process_to_mp3_check:
        process_name.text = '格式转换'
        to_mp3(old_path, music_path, logger, process_inner_list, ffmpeg_path, old_files_delete_check)
    # 切片
    if process_clip_mp3_check:
        process_name.text = '音乐切片'
        mp3_clip(music_path, music_path, logger, process_inner_list, ffmpeg_path, True)
    # 音量调整
    if process_mp3gain_check:
        process_name.text = '音量调整'
        mp3_gain(music_path, int(db_select), logger, process_inner_list, mp3gain_path)
    # 备份转换后音乐目录
    if music_path_check:
        process_name.text = '文件备份'
        update_progress(process_inner_list, 0, 1, music_path, backup_path)
        backup(music_path, backup_path, logger)
    # 随机排列
    if process_random_check:
        process_name.text = '随机排列'
        # TODO: 随机排列过程还有 label_flag 和 name_flag 两个参数，暂时未实现到界面
        mp3_random(music_path, random_path, result_txt, logger, process_inner_list,
                   remove_flag=music_files_delete_check)
    # 备份随机排列后目录
    if random_path_check:
        process_name.text = '文件备份'
        update_progress(process_inner_list, 0, 1, random_path, backup_path)
        backup(random_path, backup_path, logger)
    # 运行结束
    process_name.text = '运行结束'
    update_progress(process_inner_list, 1, 1, '', '')
    logger.info('运行结束')
    window.evaluate_js("""StopTimer();""")


def reset(window, default_input_dict, default_checked_dict):
    for input_element, default_value in default_input_dict.items():
        input_element.value = value_replace(default_value)
    for checkbox_id, default_checked in default_checked_dict.items():
        window.evaluate_js(f'document.getElementById("{checkbox_id}").checked = {str(default_checked).lower()}')


def bind(window, cwd):
    # 界面初始化
    options = get_element(window, 'options')
    options.show()
    process = get_element(window, 'process')
    process.hide()
    frame_size = (window.width - 650, window.height - 725)

    # ffmpeg 和 mp3gain 初始检查
    ffmpeg = get_element(window, 'ffmpeg')
    ffmpeg_check = get_element(window, 'ffmpeg_check')
    ffmpeg.on('click', lambda e: get_dependence_file(window, ffmpeg, ffmpeg_check, cwd,
                                                     file_types=('ffmpeg Executable File (*.exe)',)))
    ffmpeg_check.on('click', lambda e: get_dependence_file(window, ffmpeg, ffmpeg_check, cwd,
                                                           file_types=('ffmpeg Executable File (*.exe)',)))
    check_dependence_flag(ffmpeg, ffmpeg_check)
    mp3gain = get_element(window, 'mp3gain')
    mp3gain_check = get_element(window, 'mp3gain_check')
    mp3gain.on('click', lambda e: get_dependence_file(window, mp3gain, mp3gain_check, cwd,
                                                      file_types=('mp3gain Executable File (*.exe)',)))
    mp3gain_check.on('click', lambda e: get_dependence_file(window, mp3gain, mp3gain_check, cwd,
                                                            file_types=('mp3gain Executable File (*.exe)',)))
    check_dependence_flag(mp3gain, mp3gain_check)
    dependence_list = [ffmpeg, ffmpeg_check, mp3gain, mp3gain_check]

    # 输入控件初始化
    # TODO: 或可采用mom_path的选择来初始化其他路径，提供快速设置
    old_path = get_element(window, 'old_path')
    old_path.value = value_replace(cwd + '\\old')
    old_path_button = get_element(window, 'old_path_button')
    old_path_button.on('click',
                       lambda e: get_path(window, old_path, cwd, path_types=('Old Music Path',), file_types=None))

    music_path = get_element(window, 'music_path')
    music_path.value = value_replace(cwd + '\\new')
    music_path_button = get_element(window, 'music_path_button')
    music_path_button.on('click',
                         lambda e: get_path(window, music_path, cwd, path_types=('New Music Path',), file_types=None))

    db_select = get_element(window, 'db_select')

    random_path = get_element(window, 'random_path')
    random_path.value = value_replace(cwd + '\\random')
    random_path_button = get_element(window, 'random_path_button')
    random_path_button.on('click', lambda e: get_path(window, random_path, cwd, path_types=('Random Music Path',),
                                                      file_types=None))

    result_txt = get_element(window, 'result_txt')
    result_txt.value = value_replace(cwd + '\\result.txt')
    result_txt_button = get_element(window, 'result_txt_button')
    result_txt_button.on('click', lambda e: get_path(window, result_txt, cwd, path_types=None,
                                                     file_types=('Txt Files (*.txt)',)))

    backup_path = get_element(window, 'backup_path')
    backup_path.value = value_replace(cwd + '\\backup')
    backup_path_button = get_element(window, 'backup_path_button')
    backup_path_button.on('click',
                          lambda e: get_path(window, backup_path, cwd, path_types=('Backup Path',), file_types=None))

    # 默认值初始化
    input_element_list = [old_path, music_path, db_select, random_path, result_txt, backup_path]
    checked_id_list = ['old_path_check', 'music_path_check', 'random_path_check',
                       'old_files_delete_check', 'music_files_delete_check',
                       'process_to_mp3_check', 'process_clip_mp3_check', 'process_mp3gain_check',
                       'process_random_check']

    default_input_dict = {input_element: input_element.value for input_element in input_element_list}
    default_checked_dict = get_checked(window, checked_id_list)

    # 按钮绑定
    start_button = get_element(window, 'start_button')
    start_button.on('click', lambda e: start(window, input_element_list, checked_id_list, frame_size, dependence_list))
    reset_button = get_element(window, 'reset_button')
    reset_button.on('click', lambda e: reset(window, default_input_dict, default_checked_dict))
    exit_button = get_element(window, 'exit_button')
    exit_button.on('click', lambda e: window.destroy())


def main():
    cwd = os.getcwd()
    window = webview.create_window('MP3Random', 'static/index.html', width=650, height=750)
    webview.start(bind, (window, cwd))


if __name__ == '__main__':
    main()
