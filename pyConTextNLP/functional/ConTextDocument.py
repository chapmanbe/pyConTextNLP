import re
import networkx as nx
from . import ConTextMarkup
import copy

class ConTextDocument(nx.DiGraph):
    """
    base class for context.
    build around markedTargets a list of termObjects representing desired terms
    found in text and markedModifiers, tagObjects found in the text
    """
    rb = re.compile(r"""\b""", re.UNICODE)
    def __init__(self, unicodeEncoding='utf-8', currentSentenceNum=0):
        """txt is the string to parse"""
        # for each sentence and then put in the archives when the next sentence
        # is processed
        super(ConTextDocument, self).__init__(__unicodeEncoding=unicodeEncoding,
                                              __currentSentenceNum=currentSentenceNum)

        self.graph["__currentParent"] = "document"
        self.graph["__documentGraph"] = None

    #def __str__(self):
        #return unicode(self).encode('utf-8')
    #def __repr__(self):
        #return unicode(self).encode('utf-8')

def insertSection(cd, sectionLabel, setToParent=False, setToRoot=False):
    cd_new = copy.copy(cd)
    if setToRoot:
        cd_new.graph["__root"] = sectionLabel
        cd_new.add_node(sectionLabel, category="section")
    else:
        cd_new.add_node(sectionLabel, category="section")

        cd_new.add_edge(cd_new.graph["__currentParent"], sectionLabel)
    if setToParent:
        cd_new.graph["__currentParent"] = sectionLabel
    return cd_new


def getCurrentSentenceNumber(cd):
    """
    """
    return cd.graph["__currentSentenceNum"]
def setParent(cd, label=None):
    cd_new = copy.copy(cd)
    cd_new.graph["__currentParent"] = label
    return cd_new

def getCurrentparent(cd):
    return cd.graph["__currentParent"]

def addSectionattributes(cd, **kwargs):
    cd_new = copy.copy(cd)
    for key in kwargs.keys():
        cd_new.node[cd_new.graph["__currentParent"]][key] = kwargs[key]
    return cd_new
def getUnicodeEncoding(cd):
    return cd.graph["__unicodeEncoding"]

def addMarkup(cd, markup):
    """
    add the markup as a node in the document attached to the current parent.
    """
    cd_new = copy.copy(cd)
    cd_new.add_edge(cd_new.graph["__currentParent"], markup,
                    category="markup",
                    sentenceNumber=cd_new.graph["__currentSentenceNum"])

    cd_new.graph["__currentSentenceNum"] += 1
    return cd_new
def retrieveMarkup(cd, sentenceNumber):
    """
    retrieve the markup corresponding to sentenceNumber
    """
    edge = [e for e in cd.edges(data=True) if e[2]['category'] == "markup" and
                                              e[2]['sentenceNumber'] == sentenceNumber]
    if edge:
        return edge[0]

def getSectionNodes(cd, sectionLabel=None, category="markup"):
    if not sectionLabel:
        sectionLabel = cd.graph["__currentParent"]
    successors = [(e[2]['__sectionNumber'], e[1]) for e in cd.out_edges(sectionLabel, 
                                                                       data=True)
                                                     if e[2].get("category") == category]
    successors.sort()
    tmp = zip(*successors)
    return tmp

def getSectionMarkups(cd, sectionLabel=None, returnSentenceNumbers=True):
    """return the markup graphs for the section ordered by sentence number"""
    if not sectionLabel:
        sectionLabel = cd.graph["__currentParent"]
    successors = [(e[2]['sentenceNumber'], e[1]) for e in cd.out_edges(sectionLabel, 
                                                                      data=True)
                                                    if e[2].get("category") == "markup"]
    successors.sort()
    if returnSentenceNumbers:
        return successors
    else:
        tmp = zip(*successors)
        return tmp[1]

def getDocumentSections(cd):
    edges = [(e[2]['sectionNumber'], e[1]) for e in cd.edges(data=True) \
                                               if e[2].get("category") == "section"]
    edges.sort()
    tmp = zip(*edges)
    try:
        tmp = tmp[1]
        tmp.insert(0, cd.graph["__root"])
    except IndexError:
        tmp = [cd.graph["__root"]]
    return tmp

def getSectionText(cd, sectionLabel=None ):
    """
    """
    markups = cd.getSectionMarkups(sectionLabel, returnSentenceNumbers=False)
    txt = " ".join([m.getText() for m in markups])
    return txt

def getDocumentGraph(cd):
    if not cd.graph["__documentGraph"]:
        return computeDocumentGraph(cd)
    return cd.graph["__documentGraph"]

def set_documentGraph(cd):
    cd_new = copy.copy(cd)
    cd_new.graph["__documentGraph"] = computeDocumentGraph(cd)
    return cd_new


def compute_documentGraph(cd):
    """Create a single document graph from the union of the graphs created
        for each sentence in the archive. Note that the algorithm in NetworkX
        is different based on whether the Python version is greater than or
        equal to 2.6"""
    # Note that this as written does not include the currentGraph in the DocumentGraph
    documentGraph = nx.DiGraph()
    markups = [e[1] for e in cd.edges(data=True) if e[2].get('category') == 'markup']
    for i in range(len(markups)):
        m = markups[i]
        documentGraph = nx.union(m, documentGraph)

    return documentGraph
