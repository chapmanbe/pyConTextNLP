#Copyright 2010 Brian E. Chapman
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
"""
This module contains three class definitions that are used in the pyConText
algorithm. The pyConText algorithm relies on regular expressions to identify
sub-texts of interest

1) termObject: a class that describes terms of interest within the text
2) tagObject: a class inherited from termObject that describes modifiers
3) pyConText: a class that implements the context algorithm

"""
import re
from .ConTextMarkup import ConTextMarkup
from .io.xml import xmlScrub
import networkx as nx


ConTextDocumentXMLSkel=\
"""
<ConTextDocument>
{0}
</ConTextDocument>
"""


class ConTextDocument(object):
    """
    base class for context.
    build around markedTargets a list of termObjects representing desired terms
    found in text and markedModifiers, tagObjects found in the text
    """
    rb = re.compile(r"""\b""",re.UNICODE)
    def __init__(self,unicodeEncoding='utf-8'):
        """txt is the string to parse"""
        # __document capture the document level structure
        # for each sentence and then put in the archives when the next sentence
        # is processed
        self.__unicodeEncoding = unicodeEncoding
        self.__document = nx.DiGraph()
        self.__currentSentenceNum = 0
        self.__currentSectionNum = 0
        self.__document.add_node("document", category="section", __sectionNumber = self.__currentSectionNum)
        self.__currentSectionNum += 1
        self.__currentParent = "document"
        self.__root = "document"
        self.__documentGraph = None

    def insertSection(self,sectionLabel,setToParent=False):
        self.__document.add_edge(self.__currentParent,sectionLabel,category="section",__sectionNumber=self.__currentSectionNum)
        self.__currentSectionNum += 1
        if setToParent:
            self.__currentParent = sectionLabel

    def getDocument(self):
        return self.__document
    def getCurrentSentenceNumber(self):
        return self.__currentSentenceNum
    def getCurrentSectionNumber(self):
        return self.__currentSectionNum
    def setParent(self, label=None):
        self.__currentParent = label
    def getCurrentparent(self):
        return self.__currentParent
    def addSectionattributes(self,**kwargs):
        for key in kwargs.keys():
            self.__document.node[self.__currentParent][key] = kwargs[key]
    def getUnicodeEncoding(self):
        return self.__unicodeEncoding

    def addMarkup(self, markup):
        """
        add the markup as a node in the document attached to the current parent.
        """
        # I'm not sure if I want to be using copy here
        self.__document.add_edge(self.__currentParent,markup,
                category="markup",
                sentenceNumber=self.__currentSentenceNum)

        self.__currentSentenceNum += 1
    def retrieveMarkup(self,sentenceNumber):
        """
        retrieve the markup corresponding to sentenceNumber
        """
        edge = [e for e in self.__document.edges(data=True) if e[2]['category'] == "markup" and e[2]['sentenceNumber'] == sentenceNumber]
        if edge:
            return edge[0]

    def getSectionNodes(self,sectionLabel = None, category="markup"):
        if not sectionLabel:
            sectionLabel = self.__currentParent
        successors = [(e[2]['__sectionNumber'],e[1]) for e in self.__document.out_edges(sectionLabel, data=True)
                                                            if e[2].get("category") == category]
        successors.sort()
        tmp = list(zip(*successors))
        return tmp[1]

    def getSectionMarkups(self, sectionLabel = None, returnSentenceNumbers=True ):
        """return the markup graphs for the section ordered by sentence number"""
        if not sectionLabel:
            sectionLabel = self.__currentParent
        successors = [(e[2]['sentenceNumber'],e[1]) for e in self.__document.out_edges(sectionLabel, data=True)
                                                            if e[2].get("category") == "markup"]
        successors.sort()
        if returnSentenceNumbers:
            return successors
        else:
            tmp = list(zip(*successors))
            return tmp[1]

    def getDocumentSections(self):
        edges = [ (e[2]['__sectionNumber'],e[1]) for e in self.__document.edges(data=True) if e[2].get("category") == "section"]
        edges.sort()
        tmp = list(zip(*edges))
        if len(tmp) > 1:
            tmp = [self.__root, tmp[1]]
        else:
            tmp = [self.__root]
        return tmp

    def getSectionText(self,sectionLabel = None ):
        """
        """
        markups = self.getSectionMarkups(sectionLabel,returnSentenceNumbers = False)
        txt = " ".join([ m.getText() for m in markups])
        return txt

    def getDocumentGraph(self):
        if not self.__documentGraph:
            self.computeDocumentGraph()
        return self.__documentGraph

    def getXML(self):
        txt = ""
# first generate string for all the sentences from the document in order to compute document level offsets
        documentString = ""
        sentenceOffsets = {}
        sections = self.getDocumentSections()
        for s in sections:
            markups = self.getSectionMarkups(s)
            for m in markups:
                sentenceOffsets[m[0]] = len(documentString)
                documentString = documentString + m[1].getText()+" "

        txt += xmlScrub(documentString)
        # get children sections of root


        for s in sections:
            txt += """<section>\n<sectionLabel> {0} </sectionLabel>\n""".format(s)
            markups = self.getSectionMarkups(s)
            for m in markups:
                txt += "<sentence>\n<sentenceNumber> %d </sentenceNumber>\n<sentenceOffset> %d </sentenceOffset></sentence>\n%s"%(
                    (m[0],sentenceOffsets[m[0]],m[1].getXML()))
            txt += """</section>\n"""

        return ConTextDocumentXMLSkel.format(txt)
    def __unicode__(self):
        txt = '_'*42+"\n"
        return txt
    def __str__(self):
        return self.__unicode__()
    def __repr__(self):
        return self.__unicode__()#.encode('utf-8')

    def computeDocumentGraph(self, verbose=False):
        """Create a single document graph from the union of the graphs created
           for each sentence in the archive. Note that the algorithm in NetworkX
           is different based on whether the Python version is greater than or
           equal to 2.6"""
        # Note that this as written does not include the currentGraph in the DocumentGraph
        # Maybe this should be changed
        self.__documentGraph = ConTextMarkup()
        if verbose:
            print("Document markup has {0d} edges".format(self.__document.number_of_edges()))
        markups = [e[1] for e in self.__document.edges(data=True) if e[2].get('category') == 'markup']
        if verbose:
            print("Document markup has {0d} conTextMarkup objects".format(len(markups)))
        for i in range(len(markups)):
        #for m in markups:
            m = markups[i]
            if verbose:
                print("markup {0d} has {1d} total items including {2d} targets".format(i,m.number_of_nodes(),m.getNumMarkedTargets()))

            self.__documentGraph = nx.union(m,self.__documentGraph)
            if verbose:
                print("documentGraph now has {0d} nodes".format(self.__documentGraph.number_of_nodes()))




