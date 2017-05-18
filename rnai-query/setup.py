from setuptools import setup
from sys import version_info, exit

if version_info[0] == 2:
    exit("Sorry, Python 2 is not supported")


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
  name='rnai_query',
  version='0.0.1',
  author='Simon Dirmeier',
  author_email='simon.dirmeier@bsse.ethz.ch',
  license='GPLv3',
  packages=['rnai_query', 'rnai_query.filesets', 'rnai_query.dbms'],
  install_requires=[
      'pandas>=0.20.1',
      'numpy>=1.10.0',
      'pyyaml>=3.12',
      'psycopg2>=2.7.1',
      'ipython>=5.1.0'
  ],
  classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Topic :: Scientific/Engineering :: Bio-Informatics',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5'
  ]
)
