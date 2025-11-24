from setuptools import find_packages, setup

package_name = 'tondo_charger'

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
    maintainer='nuc',
    maintainer_email='nuc@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
		"arduinoMegaToRosSerial = tondo_charger.myArduino2RosSerialInterface:main",
		"tondoChargerController = tondo_charger.tondoChargerController:main"
        ],
    },
)
