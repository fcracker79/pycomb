import os
import sys

from setuptools import setup, find_packages


major, minor1, minor2, release, serial = sys.version_info

readfile_kwargs = {"encoding": "utf-8"} if major >= 3 else {}


def readfile(filename):
    with open(filename, **readfile_kwargs) as fp:
        contents = fp.read()
    return contents


def get_packages(path):
    out = [path]
    for x in find_packages(path):
        out.append('{}/{}'.format(path, x))
    
    return out

packages = get_packages('pycomb')
setup(name='pycomb',
      version='0.1.9',
      description='Python combination',
      url='https://github.com/fcracker79/pycomb',
      author='fcracker79',
      author_email='fcracker79@gmail.com',
      license='MIT',
      packages=packages,
      install_requires=readfile(os.path.join(os.path.dirname(__file__), "requirements.txt")),
      zip_safe=False,
      test_suite="pycomb.test",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ],
      keywords='type hinting validation combinator'
      )
