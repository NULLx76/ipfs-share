from setuptools import setup

setup(
    name='ipfs_share',
    packages=['ipfs_share'],
    entry_points={
        'console_scripts': ['ipfs-share=ipfs_share.cli:main']
    }
)
