from setuptools import setup

setup(
    name='caching-proxy',
    version='1.0',
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'caching-proxy=main:main',
        ],
    },
    install_requires=[
        'fastapi',
        'uvicorn',
        'requests'
    ]
)