"""Python ConText for NLP

This is a Python implementation of the ConText NLP algorithm, or at least a
subset of the algorithm. The current developed version is based on the NetworkX
package.
"""
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

doclines = __doc__.split("\n")
setup(name='pyConTextNLP',
      version='0.5.0',
      description=doclines[0],
      long_description = "\n".join(doclines[1:]),
      author='Brian Chapman',
      author_email='brchapman@ucsd.edu',
      license="http://www.apache.org/licenses/LICENSE-2.0",
      platforms = ["any"],
      url='http://code.google.com/p/negex/',
      download_url='http://code.google.com/p/negex/downloads/list',
      #py_modules = pyn,
      packages=find_packages('src'),
      package_dir={'':'src'},
      install_requires = ['networkx','nose','unicodecsv'],
     )
