from setuptools import setup, find_packages
from sys import version_info, exit


if version_info[0] == 2:
    exit("Sorry, Python 2 is not supported")


def readme():
    with open('README.rst') as fl:
        return fl.read()

setup(
  name='rnaiutilities',
  version='0.1.2',
  description='A collection of commandline tools and python modules '
              'for working with image-based RNAi screens.',
  long_description=readme(),
  url='https://github.com/dirmeier/rnaiutilities',
  author='Simon Dirmeier',
  author_email='simon.dirmeier@bsse.ethz.ch',
  license='GPLv3',
  keywords='rnai utilities microscopy cellprofiler perturbation',
  packages=find_packages(),
  scripts=['scripts/rnai-query', 'scripts/rnai-parse'],
  python_requires='>=3',
  install_requires=[
      'h5py>=2.7.0',
      'ipython>=5.1.0',
      'numpy>=1.10.0',
      'scipy>=0.19.0',
      'pandas>=0.20.1',
      'psycopg2>=2.7.1',
      'pyyaml>=3.12',
      'tables>=3.3.0',
      'click>=6.7',
      'pytest>=3.0.5',
      'tabulate>=0.7.7'
  ],
  classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Topic :: Scientific/Engineering :: Bio-Informatics',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6'
  ]
)

