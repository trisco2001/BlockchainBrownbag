from setuptools import setup, find_packages


setup(
    name='blockchainbrownbag',
    version='1.0.0',
    description='Blockchain Brownbag',
    author='Tristan Leonard',
    license='',
    classifiers=[
        'Programming Language :: Python :: 3.4'
    ],
    keywords='',
    packages=find_packages(exclude=['contrib', 'docs', 'spec*']),
    install_requires=[
        'flask',
        'requests',
    ],
    package_data={},
    data_files=[],
    entry_points={
        'console_scripts': [
            'blockchainbrownbag = blockchainbrownbag.app:main'
        ],
    },
)