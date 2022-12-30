from setuptools import find_packages, setup

setup(
    name='Discord-Qalib',
    author="Yousef Zaher",
    author_email="syberprojects@gmail.com",
    url="https://github.com/YousefEZ/discord-qalib",
    version='0.0.7',
    description='A library for templating responses on .xml, and .json files for discord.py',
    packages=find_packages(exclude=("test*",)),
)
