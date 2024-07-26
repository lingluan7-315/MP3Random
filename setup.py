from setuptools import setup, find_packages

setup(
    name='MP3Random',
    version='0.1',
    description='A random MP3 player with a GUI built using pywebview.',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/MP3Random',
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
