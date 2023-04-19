from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Discord-Qalib",
    author="Yousef Zaher",
    author_email="syberprojects@gmail.com",
    url="https://github.com/YousefEZ/discord-qalib",
    version="2.1.0",
    description="A library for templating responses on .xml, and .json files for discord.py",
    packages=find_packages(exclude=("test*",)),
    license="MIT",
    python_requires=">=3.8.0",
    install_requires=requirements,
)
