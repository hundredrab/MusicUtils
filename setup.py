from setuptools import setup

with open('README.md') as README:
    long_description = README.read()
setup(
    name='MusicUtils',
    version='0.1.dev4',
    packages=['musicutils', ],
    license='MIT',
    description='Helpful library and command-line-tool \
        to download music, update metadata, rearrange \
        files, and other common utilities.',
    long_description=long_description,
    author='Sourab Jha',
    author_email='jha.sourab@gmail.com',
    install_requires=[
        'mutagen',
        'eyed3',
        'youtube-dl',
        'lxml',
        'bs4',
        'requests'
    ],
    python_requires='>=3.4',
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points=dict(console_scripts=[
        'mutils = musicutils.utils:main', ]),
    url='https://github.com/hundredrab/musicutils',

)
