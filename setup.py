from setuptools import setup, find_packages

setup(
    name='Nova-Satellite',
    version='1.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'nova-satellite=nova_satellite.main:main'
        ]
    }
)