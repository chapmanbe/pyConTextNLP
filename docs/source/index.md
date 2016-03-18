# pyConTextNLP
## Python ConText implementation for NLP

## What is pyConTextNLP?

pyConTextNLP is a partial implementation of the ConText algorithm using Python. The original description of  pyConTextNLP was provided in Chapman BE, Lee S, Kang HP, Chapman WW, "Document-level classification of CT pulmonary angiography reports based on an extension of the ConText algorithm." [J Biomed Inform. 2011 Oct;44(5):728-37](http://www.sciencedirect.com/science/article/pii/S1532046411000621)

Since that publication pyConTextNLP has undergone several important revisions:

1. Incorporating NetworkX to describe target/modifier relationships.
1. Porting from Python 2.x to Python 3.x
    * This is a work in progress. pyConTextNLP does not have a clean transition for handling unicode in Python 2.x in my attempts to port to 3.x
1. Rewriting pyConTextNLP to have a more functional style.
    * This has been motivated by both the need to incorporate parallel processing into the algorithm for speed and to reduce unintended side effects.
    * This work currently lies in the subpackage ``functional``.


## Publications Based on pyConTextNLP

Other publications/presentations based on pyConText include:
  * Wilson RA, et al. "Automated ancillary cancer history classification for mesothelioma patients from free-text clinical reports." J Pathol Inform. 2010 Oct 11;1:24.
  * Chapman BE, Lee S, Kang HP, Chapman WW. Using ConText to Identify Candidate Pulmonary Embolism Subjects Based on Dictated Radiology Reports. (Presented at AMIA Clinical Research Informatics Summit 2011)
  * Wilson RA, Chapman WW, DeFries SJ, Becich MJ, Chapman BE. Identifying History of Ancillary Cancers in Mesothelioma Patients from Free-Text Clinical Reports. (Presented at AMIA 2010).

Note: we changed the package name from pyConText to pyConTextNLP because of a name conflict on pypi.

## Dependencies
* [NetworkX](https://pypi.python.org/pypi/networkx/) for relating ConText relationships.
* [TextBlob](https://pypi.python.org/pypi/textblob) for sentence splitting.
* [nose](https://pypi.python.org/pypi/nose/) for unit testing.

## Installation

pyConTextNLP is hosted on [GitHub](https://github.com/chapmanbe/pyConTextNLP) and is index in pypi so can be installed with pip:

``pip install pyConTextNLP``
