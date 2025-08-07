"""
Setup script for MOVA package
Скрипт налаштування для пакету MOVA
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mova",
    version="2.2.0",
    author="Leryk1981",
    author_email="leryk1981@example.com",
    description="Machine-Operable Verbal Actions - Declarative Language for LLM",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Leryk1981/MOVA",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "mova=mova.cli.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="llm, language, declarative, ai, chatbot, automation",
    project_urls={
        "Bug Reports": "https://github.com/Leryk1981/MOVA/issues",
        "Source": "https://github.com/Leryk1981/MOVA",
        "Documentation": "https://github.com/Leryk1981/MOVA#readme",
    },
) 