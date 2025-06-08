from setuptools import find_packages, setup

package_name = 'book_organizing_bot'

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
    maintainer='bako98',
    maintainer_email='bako98@todo.todo',
    description='TODO: Package description',
    license="Apache 2.0 License",
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "BookOrganizing = book_organizing_bot.BookOrganizing:main",
        ],
    },
)
