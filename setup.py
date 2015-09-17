
from setuptools import setup

setup(name='epflmanager',
      version='0.1',
      description='Add commands to ease the day-to-day operations at EPFL',
      url='http://github.com/RomainGehrig/EPFLManager',
      author='Romain Gehrig',
      author_email='romain.gehrig@epfl.ch',
      license='MIT',
      packages=['epflmanager'],
      scripts=['bin/epfl'],
      zip_safe=False)
