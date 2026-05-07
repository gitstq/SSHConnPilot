#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSHConnPilot - Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="sshconnpilot",
    version="1.0.0",
    author="SSHConnPilot Team",
    author_email="",
    description="Lightweight AI-Powered SSH Connection Intelligence Manager CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/SSHConnPilot",
    py_modules=["sshconnpilot"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sshconnpilot=sshconnpilot:main",
            "sshcp=sshconnpilot:main",
        ],
    },
    keywords="ssh cli terminal remote-server connection-manager ai productivity",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/SSHConnPilot/issues",
        "Source": "https://github.com/gitstq/SSHConnPilot",
    },
)
