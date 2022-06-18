from setuptools import setup

setup(name='gcc_flags',
      version='0.1.0',
      author='Niels Lohmann',
      author_email='mail@nlohmann.me',
      maintainer='Niels Lohmann',
      maintainer_email='mail@nlohmann.me',
      url='https://github.com/nlohmann/gcc_flags',
      description='Collect GCC C++ warning options',
      license='MIT',
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: C++',
            'Topic :: Software Development :: Compilers'
      ],
      packages=['gcc_flags'],
      scripts=['gcc_flags/gcc_flags'],
      install_requires=['termcolor'],
      include_package_data=True,
      zip_safe=False)
