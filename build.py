# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# 凌乱之主
# 2024年07月29日
import subprocess


def build():
    cmd = ('pyinstaller --name=MP3Random --hidden-import=pythonnet --icon=mp3ramdom/static/icon.ico'
           ' --add-data=mp3random/static;static -F -w mp3random/main.py')
    subprocess.run(cmd, shell=True)


if __name__ == '__main__':
    print('build')
    build()
