#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

setup(
    name='hackertarget',
    version='3.0.0',
    description='HackerTarget CLI - Network reconnaissance and security testing toolkit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ismailtasdelen/hackertarget',
    author='İsmail Taşdelen',
    author_email='pentestdatabase@gmail.com',
    license='MIT',
    packages=find_packages(),
    package_data={
        '': ['*.yaml', '*.yml'],
    },
    install_requires=[
        'requests>=2.31.0',
        'pyyaml>=6.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'flake8>=6.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'hackertarget=source.cli:main',
        ],
    },
    python_requires='>=3.7',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
    ],
    keywords='security, networking, reconnaissance, pentesting, hackertarget, osint',
)
