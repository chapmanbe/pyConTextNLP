import re
import networkx as nx
from ConTextMarkup import ConTextMarkup

from utils import xmlScrub

ConTextDocumentXMLSkel=u"""
<ConTextDocument>
%s
</ConTextDocument>
"""

class ConTextDocument(nx.DiGraph):
    """
    base class for context.
    build around markedTargets a list of termObjects representing desired terms
    found in text and markedModifiers, tagObjects found in the text
    """
    rb = re.compile(r"""\b""",re.UNICODE)
    def __init__(self,unicodeEncoding='utf-8', currentSentenceNum=0):
        """txt is the string to parse"""
        # for each sentence and then put in the archives when the next sentence
        # is processed
        super(ConTextDocument,self).__init__(__unicodeEncoding=unicodeEncoding,
                                   __currentSentenceNum=currentSentenceNum)
                                   
        self.graph["__currentParent"] = "document"
        self.__documentGraph = None

    def insertSection(self,sectionLabel,setToParent=False, setToRoot=False):
        if setToRoot:
            self.graph["__root"] = sectionLabel
            self.add_node(sectionLabel,category="section")
        else:
            self.add_node(sectionLabel, category="section")

            self.add_edge(self.graph["__currentParent"],sectionLabel)
        if setToParent:
            self.graph["__currentParent"] = self.node(sectionLabel)


    def getCurrentSentenceNumber(self):
        """
        >>> cd = ConTextDocument()
        >>> cd.getCurrentSentenceNumber()
        0
        """
        return self.graph["__currentSentenceNum"]
    def setParent(self, label=None):
        self.__currentParent = label
    def getCurrentparent(self):
        return self.graph["__currentParent"]
    def addSectionattributes(self,**kwargs):
        for key in kwargs.keys():
            self.node[self.graph["__currentParent"]][key] = kwargs[key]
    def getUnicodeEncoding(self):
        return self.graph["__unicodeEncoding"]

    def addMarkup(self, markup):
        """
        add the markup as a node in the document attached to the current parent.
        """
        # I'm not sure if I want to be using copy here
        self.add_edge(self.graph["__currentParent"],markup,
                category="markup",
                sentenceNumber=self.graph["__currentSentenceNum"])

        self.graph["__currentSentenceNum"] += 1
    def retrieveMarkup(self,sentenceNumber):
        """
        retrieve the markup corresponding to sentenceNumber
        """
        edge = [e for e in self.edges(data=True) if e[2]['category'] == "markup" and e[2]['sentenceNumber'] == sentenceNumber]
        if edge:
            return edge[0]

    def getSectionNodes(self,sectionLabel = None, category="markup"):
        if not sectionLabel:
            sectionLabel = self.graph["__currentParent"]
        successors = [(e[2]['__sectionNumber'],e[1]) for e in self.out_edges(sectionLabel, data=True)
                                                            if e[2].get("category") == category]
        successors.sort()
        tmp = zip(*successors)
        return tmp

    def getSectionMarkups(self, sectionLabel = None, returnSentenceNumbers=True ):
        """return the markup graphs for the section ordered by sentence number"""
        if not sectionLabel:
            sectionLabel = self.__currentParent
        successors = [(e[2]['sentenceNumber'],e[1]) for e in self.out_edges(sectionLabel, data=True)
                                                            if e[2].get("category") == "markup"]
        successors.sort()
        if returnSentenceNumbers:
            return successors
        else:
            tmp = zip(*successors)
            return tmp[1]

    def getDocumentSections(self):
        edges = [ (e[2]['sectionNumber'],e[1]) for e in self.edges(data=True) if e[2].get("category") == "section"]
        edges.sort()
        tmp = zip(*edges)
        try:
            tmp = tmp[1]
            tmp.insert(0,self.__root)
        except IndexError:
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
        txt = u""
# first generate string for all the sentences from the document in order to compute document level offsets
        documentString = u""
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
            txt += u"""<section>\n<sectionLabel> %s </sectionLabel>\n"""%s
            markups = self.getSectionMarkups(s)
            for m in markups:
                txt += u"<sentence>\n<sentenceNumber> %s </sentenceNumber>\n<sentenceOffset> %s </sentenceOffset></sentence>\n%s"%(m[0],sentenceOffsets[m[0]],m[1].getXML())
            txt += u"""</section>\n"""

        return ConTextDocumentXMLSkel%txt
    #def __unicode__(self):
    #   txt = u'_'*42+"\n"
    #   return txt
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __repr__(self):
        return unicode(self).encode('utf-8')


    def computeDocumentGraph(self, verbose=False):
        """Create a single document graph from the union of the graphs created
           for each sentence in the archive. Note that the algorithm in NetworkX
           is different based on whether the Python version is greater than or
           equal to 2.6"""
        # Note that this as written does not include the currentGraph in the DocumentGraph
        # Maybe this should be changed
        self.__documentGraph = ConTextMarkup()
        if verbose:
            print("Document markup has %d edges"%self.number_of_edges())
        markups = [e[1] for e in self.edges(data=True) if e[2].get('category') == 'markup']
        if verbose:
            print("Document markup has %d conTextMarkup objects"%len(markups))
        for i in range(len(markups)):
        #for m in markups:
            m = markups[i]
            if verbose:
                print("markup %d has %d total items including %d targets"%(i,m.number_of_nodes(),m.getNumMarkedTargets()))

            self.__documentGraph = nx.union(m,self.__documentGraph)
            if verbose:
                print("documentGraph now has %d nodes"%self.__documentGraph.number_of_nodes())



# In[ ]:



