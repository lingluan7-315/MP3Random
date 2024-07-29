from setuptools import setup, find_packages

setup(
    name='MP3Random',
    version='1.0',
    description='Random music files by index',
    author='Ling Luan',
    author_email='2021051531@nwafu.edu.cn',
    url='https://github.com/lingluan7-315/MP3Random',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pywebview',
        'pyinstaller',
        # 添加其他依赖项
    ],
    entry_points={
        'console_scripts': [
            'mp3random=mp3random.main:main',  # 指定入口点
        ],
    },
)
