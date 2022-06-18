from setuptools import setup

setup(name='gcc_flags',
      version='0.1.0',
      description='gcc_flags',
      url='https://github.com/nlohmann/gcc_flags',
      packages=['gcc_flags'],
      scripts=['gcc_flags/gcc_flags'],
      install_requires=['termcolor'],
      include_package_data=True,
      zip_safe=False)
