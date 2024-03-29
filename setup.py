from setuptools import setup
from setuptools import find_packages

packages = find_packages()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-mc-lib",  # PyPI上的包名
    packages=packages,  # 包含的Python模块或子包
    version="0.1.2",  # 版本号
    author="PYmili",  # 作者
    author_email="mc2005wj@163.com",
    description="一款专为简化Minecraft整合开发而设计的Python库。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PYmili/py-mc-lib",
    classifiers=[  # 可选，用于描述项目的元数据
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',  # 可选，指定支持的Python版本
    install_requires=[
        "requests",
        "loguru"
    ],
)