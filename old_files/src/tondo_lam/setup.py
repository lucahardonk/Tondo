from setuptools import find_packages, setup

package_name = 'tondo_lam'

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
        	"telegram_skill = tondo_lam.telegram_skill:main",
        	"tondo_chatter = tondo_lam.tondo_chatter:main",
        	"tts_skill = tondo_lam.tts_skill:main"
        ],
    },
)
