pyConTextNLP
============

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

Download pyConTextNLP from GitHub at
https://github.com/chapmanbe/pyConTextNLP or the pypi repository
http://pypi.python.org/pypi/pyConTextNLP. Since pyConTextNLP is
registered with pypi, it can be installed with easy\_install or pip:

.. code:: shell

    easy_install pyConTextNLP
    pip install pyConTextNLP

Dependencies include - unicodecsv - textblob - networkx

But ``easy_install`` should also install everything for you. There is
optional functionality that is dependent on pygraphviz. I do not yet
have this worked into the setuptools script.

Tutorials
---------

See the `notebooks folder <./notebooks>`__ for a series of walkthroughs
demonstrating pyConTextNLP core concepts with example data.

Code Structure
--------------

The code has been modified substantially since the code base used for
the JBI publication. In the current version, pyConTextNLP corresponds to
pyConTextGraph in previous versions. This code uses
[https://networkx.github.io/ NetworkX] to structure the relationship
between targets and modifiers in the markup.

The package has three files:

-  *itemData.py*. This is where the essential domain knowledge is stored
   in 4-tuples as described in the paper. For a new application, this is
   where the user will encapsulate the domain knowledge for their
   application.
-  *pyConTextGraph.py*. This module defines the algorithm
-  *pyConTextSql.py*.

How to Use
----------

I am working on improving the documentation and (hopefully) adding some
testing to the code.

Some preliminary comments:

-  pyConTextNLP works marks up text on a sentence by sentence level.
-  pyConTextNLP facilitates reasoning from multi-sentence documents, but
   the markup (e.g. negation is all limited within the scope of a
   sentence.
-  pyConTextNLP assumes the sentence is a string not a list of words

The Skeleton of an Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

To illustrate how to use pyConTextNLP, I've taken some code excerpts
from a simple application, *criticalFinderGraph.py*, that was written to
identify critical finders in radiology reports.

The first step in building an application is to define ``itemData``
objects for your problem. The package contains ``itemData`` objects
defined in ``pyConTextNLP.pyConText.itemData``. Common negation terms,
conjunctions, pseudo-negations, etc. are defined in here. An itemData
instance consists of a 4-tuple. Here is an excerpt defining two
``itemData`` objects:

.. code:: python

    probableNegations = itemData([
      "can rule out",
      "PROBABLE_NEGATED_EXISTENCE",
      "",
      "forward"
    ],
    [
      "cannot be excluded",
      "PROBABLE_NEGATED_EXISTENCE",
      r"""cannot\sbe\s((entirely|completely)\s)?(excluded|ruled out)""",
      "backward"
    ])

The four parts are

1. The ``literal`` "can rule out", "cannot be excluded"
2. The ``category`` "PROBABLE\_NEGATED\_EXISTENCE"
3. The ``regular expression`` (optional) used to capture the literal in
   the text. If no regular expression is provided, a regular expression
   is generated literally from the literal.
4. The ``rule`` (optional). If the ``itemData`` is being used as a
   modifier, the rule states what direction the modifier operates in the
   sentence: current valid values are: "forward", the item can modify
   objects following it in the sentence; "backward", the item can modify
   objects preceding it in the sentence; or "bidirectional", the item
   can modify objects preceding and following it in the sentence.

For the *criticalFinderGraph.py* application, we defined ``itemData``
for the critical findings we wanted to identify in the text, for example
pulmonary emboli and aortic dissections. These new ``itemData`` objects
were defined in a file named *critfindingItemData.py*:

.. code:: python

    critItems = itemData(
    ['pulmonary embolism','PULMONARY_EMBOLISM',r'''pulmonary\s(artery )?(embol[a-z]+)''',''],
    ['pe','PULMONARY_EMBOLISM',r'''\bpe\b''',''],
    ['embolism','PULMONARY_EMBOLISM',r'''\b(emboli|embolism|embolus)\b''',''],
    ['aortic dissection','AORTIC_DISSECTION','',''])

We also added negation terms that were not originally defined in
pyConTextNLP:

.. code:: python

    definiteNegations.prepend([["nor","DEFINITE_NEGATED_EXISTENCE","","forward"],])

Once we have all our ``itemData`` defined, we're now ready to start
processing text.

In our application we need to import the relevant modules from
pyConTextNLP as well as our own ``itemData`` definitions:

.. code:: python

    import pyConTextNLP.pyConTextGraph.pyConTextGraph as pyConText
    import pyConText.helpers as helpers
    from critfindingItemData import *

Assuming we have read in our documents to process and that the basic
document unit is a ``report`` we can write a simple function to process
the report

.. code:: python

    def analyzeReport(report, targets, modifiers ):
        """given an individual radiology report, markup the report based on targets and modifiers"""
        # create the pyConText instance
        context = pyConText.pyConText()

        # split the report into individual sentences. Note this is a very simple sentence splitter. You probably
        # want to write your own or use a sentence splitter from nltk or the like.
        sentences = helpers.sentenceSplitter(report)

        # process each sentence in the report
        for s in sentences:
            context.setTxt(s)
            context.markItems(modifiers, mode="modifier")
            context.markItems(targets, mode="target")

            # some itemData are subsets of larger itemData instances. At the point they will have all been
            # marked. Drop any marked targets and modifiers that are a proper subset of another marked
            # target or modifier
            context.pruneMarks()

            # drop any marks that have the CATEGORY "Exclusion"; these are phrases we want to ignore.
            context.dropMarks('Exclusion')

            # match modifiers to targets
            context.applyModifiers()

            # Drop any modifiers that didn't get hooked up with a target
            context.dropInactiveModifiers()

            # put the current markup into an "archive". The archive will later be used to reason across the entire report.


        return context

The markup is stored as a directed graph, so determining whether a
target is, for example, negated, you simply check to see if an immediate
predecessor of the target node is a negation. This is all done with
`NetworkX <https://networkx.github.io/>`__ commands.

To access the underlying graph from the context object evoke the
``getCurrentGraph()`` method

.. code:: python

    g = context.getCurrentGraph()

Here is some code to get a list of all the target nodes in the markup:

.. code:: python

    targets = [n[0] for n in g.nodes(data = True) if n[1].get("category","") == 'target']

Here is a function to test whether a node is modified by any of the
categories in a list

.. code:: python

    def modifies(g,n,modifiers):
        """g: directed graph representing the ConText markup
            n: a node in g
            modifiers: a list of categories e.g. ["definite_negated_existence","probable_existence"]
            modifies() tests whether n is modified by an objects with category in categories"""
        pred = g.predecessors(n)
        if( not pred ):
            return False
        pcats = [n.getCategory().lower() for n in pred]
        return bool(set(pcats).intersection([m.lower() for m in modifiers]))
