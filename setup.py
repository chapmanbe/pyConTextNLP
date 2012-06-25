import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(name='pyConText',
      version='0.2.8',
      description='Python ConText',
      author='Brian Chapman',
      author_email='brchapman@ucsd.edu',
      url='http://www.dbmi.pitt.edu',
      #py_modules = pyn,
      packages=find_packages('src'),
      package_dir={'':'src'},
      install_requires = ['python>=2.3','networkx>=1.0'],      
     )
