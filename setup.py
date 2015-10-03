
from setuptools import setup
from pip.req import parse_requirements
import pip

requirements = parse_requirements("requirements.txt", session=pip.download.PipSession())

setup(name='epflmanager',
      version='0.1',
      description='Add commands to ease the day-to-day operations at EPFL',
      url='http://github.com/RomainGehrig/EPFLManager',
      author='Romain Gehrig',
      author_email='romain.gehrig@epfl.ch',
      license='MIT',
      packages=['epflmanager'],
      scripts=['bin/epfl'],
      install_requires=[str(r.req) for r in requirements],
      zip_safe=False)
