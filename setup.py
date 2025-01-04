from setuptools import setup, find_packages

setup(
    name="bufo-bot",
    version="0.1",
    packages=find_packages(),
    description="bufo-boba",
    author="Matthew Ding",
    install_requires=[
        "discord.py",
        "pydantic",
        "PyNaCl",
        "python-dotenv",
    ],
)