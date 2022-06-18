from setuptools import setup
import pkg_resources
import pathlib

with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(name='gcc_flags',
      version='0.1.0',
      description='gcc_flags',
      url='https://github.com/nlohmann/gcc_flags',
      packages=['gcc_flags'],
      scripts=['gcc_flags/gcc_flags'],
      install_requires=install_requires,
      include_package_data=True,
      zip_safe=False)
