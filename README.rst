pyConTextNLP
============

This code has been validated using the included notebooks on Python v 3.7.2. Python 2.x is no longer supported.

pyConTextNLP is a Python implementation/extension/modification of the
ConText algorithm described in `CITE <>`__ which is itself a
generalization of the NegEx algorithm described in `CITE <>`__.

The package is maintained by Brian Chapman at the University of Utah.
Other active and past developers include:

-  Wendy W. Chapman
-  Glenn Dayton
-  Danielle Mowery

Introduction
------------

pyConTextNLP is a partial implementation of the ConText algorithm using
Python. The original description of pyConTextNLP was provided in Chapman
BE, Lee S, Kang HP, Chapman WW, "Document-level classification of CT
pulmonary angiography reports based on an extension of the ConText
algorithm." `J Biomed Inform. 2011
Oct;44(5):728-37 <http://www.sciencedirect.com/science/article/pii/S1532046411000621>`__

Other publications/presentations based on pyConText include: \* Wilson
RA, et al. "Automated ancillary cancer history classification for
mesothelioma patients from free-text clinical reports." J Pathol Inform.
2010 Oct 11;1:24. \* Chapman BE, Lee S, Kang HP, Chapman WW. "Using
ConText to Identify Candidate Pulmonary Embolism Subjects Based on
Dictated Radiology Reports." (Presented at AMIA Clinical Research
Informatics Summit 2011) \* Wilson RA, Chapman WW, DeFries SJ, Becich
MJ, Chapman BE. "Identifying History of Ancillary Cancers in
Mesothelioma Patients from Free-Text Clinical Reports." (Presented at
AMIA 2010).

Note: we changed the package name from pyConText to pyConTextNLP because
of a name conflict on pypi.

Installation
------------

Latest Version
~~~~~~~~~~~~~~

The latest version of pyConTextNLP is available on [github](https://github.com/chapmanbe/pyConTextNLP). 
The package can be installed by either cloning the repository and running `python setup.py install`. 
Alternatively or by
.. code:: shell
    pip install git+https://github.com/chapmanbe/pyConTextNLP.git 

PyPi
~~~~~

pyConTextNLP is also available via the Python Package Index and can be installed via

.. code:: shell

    pip install pyConTextNLP

Dependencies include 

* networkx
* PyYAML


Tutorials
---------

See the `notebooks folder <./notebooks>`__ for a series of walkthroughs
demonstrating pyConTextNLP core concepts with example data.


How to Use
----------

I am working on improving the documentation and (hopefully) adding some
testing to the code.

Some preliminary comments:

-  pyConTextNLP works marks up text on a sentence by sentence level.
-  pyConTextNLP assumes the sentence is a string not a list of words
- Our preferred way to represent knowledge is now with YAML files rather than TSV files.

