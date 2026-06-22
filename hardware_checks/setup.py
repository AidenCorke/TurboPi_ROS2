from setuptools import find_packages, setup

package_name = 'hardware_checks'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aiden',
    maintainer_email='aiden.corke@gmail.com',
    description='Package containing functions to check hardware functionality and communication',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'uart_check = hardware_checks.uart_check:main',
            'mecanum_kinematics = hardware_checks.mecanum_kinematics:main',
            'motor_driver = hardware_checks.motor_driver:main',
        ],
    },
)
