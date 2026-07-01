from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Package index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        
        # Package Manifest        
        ('share/' + package_name, ['package.xml']),

        # URDF Directory
        ('share/' + package_name + '/urdf', glob('urdf/*')),

        # RViz Configs
        ('share/' + package_name + '/rviz', glob('rviz/*')),
             
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aidencorke',
    maintainer_email='aiden.corke@gmail.com',
    description='This package contains robot description files.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
