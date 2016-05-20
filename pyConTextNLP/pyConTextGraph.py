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
import copy
import networkx as nx
import platform
import copy
import uuid

r1 = re.compile(r"""\W""",re.UNICODE)
r2 = re.compile(r"""\s+""",re.UNICODE)
r3 = re.compile(r"""\d""",re.UNICODE)

rlt = re.compile(r"""<""",re.UNICODE)
ramp = re.compile(r"""&""",re.UNICODE)

compiledRegExprs = {}

def xmlScrub(tmp):
    return rlt.sub(r"&lt;",ramp.sub(r"&amp;",u"{0}".format(tmp)))
tagObjectXMLSkel=\
u"""
<tagObject>
<id> {0} </id>
<phrase> {1} </phrase>
<literal> {2} </literal>
<category> {3} </category>
<spanStart> {4:d} </spanStart>
<spanStop> {5:d} </spanStop>
<scopeStart> {6:d} </scopeStart>
<scopeStop> {7:d} </scopeStop>
</tagObject>
"""

ConTextMarkupXMLSkel = \
u"""
<ConTextMarkup>
<rawText> {0} </rawText>
<cleanText> {1} </cleanText>
<nodes>
{2}
</nodes>
<edges>
{3}
</edges>
</ConTextMarkup>
"""
edgeXMLSkel=\
u"""
<edge>
<startNode> {0} </startNode>
<endNode> {1} </endNode>
{2}
</edge>
"""
nodeXMLSkel=\
u"""
<node>
{0}
</node>
"""

ConTextDocumentXMLSkel=\
u"""
<ConTextDocument>
{0}
</ConTextDocument>
"""
class tagObject(object):
    """
    A class that describes terms of interest in the text.
    tagObject is characterized by the following attributes
    1) The contextItem defining the tag
    3) The location of the tag within the text being parsed

    """
    def __init__(self, item, ConTextCategory,scope=None, tagid=None, **kwargs):
        """
        item: contextItem used to generate term
        ConTextCategory: category this term is being used for in pyConText

        variants
        """
        self.__item = item
        self.__category = self.__item.getCategory()
        self.__spanStart = 0
        self.__spanEnd = 0
        self.__foundPhrase = ''
        self.__foundDict = {}
        self.__ConTextCategory = ConTextCategory
        if not tagid:
            tagid = uuid.uid1().int
        self.__tagID = tagid
        if scope == None:
            self.__scope = []
        else:
            self.__scope = list(scope)
        self.__SCOPEUPDATED = False
    def setScope(self):
        """
        applies the objects own rule and span to modify the object's scope
        Currently only "forward" and "backward" rules are implemented
        """

        if 'forward' in self.__item.getRule().lower():
            self.__scope[0] = self.getSpan()[1]
        elif 'backward' in self.__item.getRule().lower():
            self.__scope[1] = self.getSpan()[0]

    def getTagID(self):
        return self.__tagID
    def parseRule(self):
        """parse the rule for the associated"""
        pass
    def getScope(self):
        return self.__scope
    def getRule(self):
        return self.__item.getRule()

    def limitScope(self,obj):
        """If self and obj are of the same category or if obj has a rule of
        'terminate', use the span of obj to
        update the scope of self
        returns True if a obj modified the scope of self"""
        if not self.getRule() or self.getRule()== 'terminate' or \
             (not self.isA(obj.getCategory()) and obj.getRule() != 'terminate'):
            return False
        originalScope = copy.copy((self.getScope()))
        if 'forward' in self.getRule().lower() or \
            'bidirectional' in self.getRule().lower():
            if obj > self:
                self.__scope[1] = min(self.__scope[1],obj.getSpan()[0])
        elif 'backward' in self.getRule().lower() or \
              'bidirectional' in self.getRule().lower():
            if obj < self:
                self.__scope[0] = max(self.__scope[0],obj.getSpan()[1])
        if originalScope != self.__scope:
            return True
        else:
            return False

    def applyRule(self,term):
        """applies self's rule to term. If the start of term lines within
        the span of self, then term may be modified by self"""
        if not self.getRule() or self.getRule() == 'terminate':
            return False
        if self.__scope[0] <= term.getSpan()[0] <= self.__scope[1]:
            return True #term.updateModifiedBy(self)
    def getConTextCategory(self):
        return self.__ConTextCategory
    def getXML(self):
        return   tagObjectXMLSkel.format(self.getTagID(),xmlScrub(self.getPhrase()),
                                   xmlScrub(self.getLiteral()),xmlScrub(self.getCategory()),
                                   self.getSpan()[0],self.getSpan()[1],
                                   self.getScope()[0],self.getScope()[1])

    def getBriefDescription(self):
        description = u"""<id> {0} </id> """.format(self.getTagID())
        description+= u"""<phrase> {0} </phrase> """.format(self.getPhrase())
        description+= u"""<category> {0} </category> """.format(self.getCategory())
        return description
    def getLiteral(self):
        """returns the term defining this object"""
        return self.__item.getLiteral()
    def getCategory(self):
        """returns the category (e.g. CONJUNCTION) for this object"""
        return self.__category[:]
    def categoryString(self):
        return u'_'.join(self.__category)
    def isA(self,category):
        return self.__item.isA(category)
    def setCategory(self,category):
        self.__category = category
    def replaceCategory(self,oldCategory,newCategory):
        for index, item in enumerate(self.__category):
            if item == oldCategory.lower().strip():
                try:
                    self.__category[index] = newCategory.lower().strip()
                except:
                    del self.__category[index]
                    self.__category.extend([nc.lower().strip() for nc in newCategory])

    def setSpan(self,span):
        """set the span within the associated text for this object"""
        self.__spanStart = span[0]
        self.__spanEnd = span[1]
    def getSpan(self):
        """return the span within the associated text for this object"""
        return self.__spanStart,self.__spanEnd
    def setPhrase(self,phrase):
        """set the actual matched phrase used to generate this object"""
        self.__foundPhrase = phrase
    def getPhrase(self):
        """return the actual matched phrase used to generate this object"""
        return self.__foundPhrase
    def setMatchedGroupDictionary(self,mdict):
        """set the foundDict variable to mdict. This gets the name/value pair for each NAMED group within the regular expression"""
        self.__foundDict = mdict.copy()
    def getMatchedGroupDictionary(self):
        """return a copy of the matched group dictionary"""
        return self.__foundDict.copy()
    def dist(self,obj):
        """returns the minimum distance from the current object and obj.
        Distance is measured as current start to object end or current end to object start"""
        return min(abs(self.__spanEnd-obj.__spanStart),abs(self.__spanStart-obj.__spanEnd))

    def __lt__(self,other): return self.__spanStart < other.__spanStart
    def __le__(self,other): return self.__spanStart <= other.__spanStart
    def __eq__(self,other):
        return (self.__spanStart == other.__spanStart and
                self.__spanEnd == other.__spanEnd)
    def __ne__(self,other): return self.__spanStart != other.__spanStart
    def __gt__(self,other): return self.__spanStart > other.__spanStart
    def __ge__(self,other): return self.__spanStart >= other.__spanStart

    def __hash__(self):
        return hash(repr(self))
    def encompasses(self,other):
        """tests whether other is completely encompassed with the current object
           ??? should we not prune identical span tagObjects???"""
        if self.__spanStart <= other.__spanStart and \
           self.__spanEnd >= other.__spanEnd:
            return True
        else:
             return False
    def overlap(self,other):
        """
        tests whether other overlaps with self
        """
        if (other.__spanStart >= self.__spanStart and other.__spanStart <= self.__spanEnd ) or \
           (other.__spanEnd >= self.__spanStart and other.__spanEnd <= self.__spanEnd):
            return True
        else:
            return False

    def leftOverlap(self,other):
        """
        tests whether other has partial overlap to the left with self.
        """
        if self.encompasses(other):
            return False
        if self.overlap(other) and self.__gt__(other):
            return True
        else:
            return False
    def rightOverlap(self,other):
        """
        tests whether other has partial overlap to the right with self
        """
        if self.encompasses(other):
            return False
        if self.overlap(other) and self.__lt__(other):
            return True
        else:
            return False

    def __unicode__(self):
        txt = self.getBriefDescription()
        return txt
    def __str__(self):
        return self.__unicode__()#.encode('utf-8')
    def __repr__(self):
        return self.__unicode__()#.encode('utf-8')
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
            txt += u"""<section>\n<sectionLabel> {0} </sectionLabel>\n""".format(s)
            markups = self.getSectionMarkups(s)
            for m in markups:
                txt += u"<sentence>\n<sentenceNumber> %d </sentenceNumber>\n<sentenceOffset> %d </sentenceOffset></sentence>\n%s"%(
                    (m[0],sentenceOffsets[m[0]],m[1].getXML()))
            txt += u"""</section>\n"""

        return ConTextDocumentXMLSkel.format(txt)
    def __unicode__(self):
        txt = u'_'*42+"\n"
        return txt
    def __str__(self):
        return self.__unicode__()
    def __repr__(self):
        return self.__unicode__()#.encode('utf-8')
    def getConTextModeNodes(self,mode):
        """
        Deprecated. This functionality should be accessed via the ConTextMarkup object now returned from getDocumentGraph()
        """
        print("This function is deprecated and will be eliminated shortly.")
        print("The same functionality can be accessed through the ConTextMarkup object returned from getDocumentGraph()")
        nodes = [n[0] for n in self.__documentGraph.nodes(data=True) if n[1]['category'] == mode]
        nodes.sort()
        return nodes

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
        ic = 0
        for i in range(len(markups)):
        #for m in markups:
            m = markups[i]
            if verbose:
                print("markup {0d} has {1d} total items including {2d} targets".format(i,m.number_of_nodes(),m.getNumMarkedTargets()))

            self.__documentGraph = nx.union(m,self.__documentGraph)
            if verbose:
                print("documentGraph now has {0d} nodes".format(self.__documentGraph.number_of_nodes()))

class ConTextMarkup(nx.DiGraph):
    """
    base class for context document.
    build around markedTargets a list of termObjects representing desired terms
    found in text and markedModifiers, tagObjects found in the text
    """
    def __init__(self,txt=u'',unicodeEncoding='utf-8'):
        """txt is the string to parse"""
        # __document capture the document level structure
        # for each sentence and then put in the archives when the next sentence
        # is processed
        super(ConTextMarkup,self).__init__(__txt=None,__rawtxt=txt,__scope=None,__SCOPEUPDATED=False)
        self.__document = nx.DiGraph()
        self.__document.add_node("top",category="document")
        self.__VERBOSE = False
        self.__tagID = 0
        self.__unicodeEncoding = unicodeEncoding

    def getUnicodeEncoding(self):
        return self.__unicodeEncoding

    def getNextTagID(self):
        return uuid.uuid1().int
        return u"%06d"%self.__tagID
    def toggleVerbose(self):
        """toggles the boolean value for verbose mode"""
        self.__VERBOSE = not self.__VERBOSE
    def getVerbose(self):
        return self.__VERBOSE

    def setRawText(self,txt=u''):
        """
        sets the current txt to txt and resets the current attributes to empty
        values, but does not modify the object archive
        """
        if self.getVerbose():
            print("Setting text to",txt)
        self.graph["__rawTxt"] = txt
        self.graph["__txt"] = None
        self.graph["__scope"] = None
        self.graph["__SCOPEUPDATED"] = False

    def getText(self):
        return self.graph.get("__txt",u'')
    def getScope(self):
        return self.graph.get("__scope",u'')
    def getScopeUpdated(self):
        return self.graph.get("__SCOPEUPDATED")
    def getRawText(self):
        return self.graph.get("__rawTxt",u'')
    def getNumberSentences(self): # !!! Need to rewrite this to match graph
        return len(self.__document)
    def cleanText(self,stripNonAlphaNumeric=False, stripNumbers=False):
        """Need to rename. applies the regular expression scrubbers to rawTxt"""
        if stripNonAlphaNumeric:
            txt = r1.sub(" ",self.getRawText() )
        else:
            txt = self.getRawText()

        # clean up white spaces
        txt = r2.sub(" ",txt)
        if stripNumbers:
            txt = r3.sub("",txt)

        self.graph["__scope"] = (0,len(txt))
        self.graph["__txt"] = txt
        if self.getVerbose():
            print(u"cleaned text is now",self.getText())
    def getXML(self):
        nodes = self.nodes(data=True)
        nodes.sort()
        nodeString = u''
        for n in nodes:
            attributeString = u''
            keys = list(n[1].keys())
            keys.sort()
            for k in keys:
                attributeString += """<{0}> {1} </{2}>\n""".format(k,n[1][k],k)
            modificationString = u''
            modifiedBy = self.predecessors(n[0])
            if modifiedBy:
                for m in modifiedBy:
                    modificationString += u"""<modifiedBy>\n"""
                    modificationString += u"""<modifyingNode> {0} </modifyingNode>\n""".format(m.getTagID())
                    modificationString += u"""<modifyingCategory> {0} </modifyingCategory>\n""".format(m.getCategory())
                    modificationString += u"""</modifiedBy>\n"""
            modifies = self.successors(n[0])
            if modifies:
                for m in modifies:
                    modificationString += u"""<modifies>\n"""
                    modificationString += u"""<modifiedNode> {0} </modifiedNode>\n""".format(m.getTagID())
                    modificationString += u"""</modifies>\n"""
            nodeString += nodeXMLSkel.format(attributeString+"{0}".format(n[0].getXML())+modificationString )
        edges = self.edges(data=True)
        edges.sort()
        edgeString = u''
        for e in edges:
            keys = list(e[2].keys())
            keys.sort()
            attributeString = u''
            for k in keys:
                attributeString += """<{0}> {1} </{2}>\n""".format(k,e[2][k],k)
            edgeString += "{0}".format(edgeXMLSkel.format(e[0].getTagID(),e[1].getTagID(),attributeString))

        return ConTextMarkupXMLSkel.format(xmlScrub(self.getRawText()),xmlScrub(self.getText()),
                                       nodeString,edgeString)
    def __unicode__(self):
        txt = u'_'*42+"\n"
        txt += 'rawText: {0}\n'.format(self.getRawText())
        txt += 'cleanedText: {0}\n'.format(self.getText())
        nodes = [n for n in self.nodes(data=True) if n[1].get('category','') == 'target']
        nodes.sort()
        for n in nodes:
            txt += "*"*32+"\n"
            txt += "TARGET: {0}\n".format(n[0].__unicode__())
            modifiers = self.predecessors(n[0])
            modifiers.sort()
            for m in modifiers:
                txt += "-"*4+"MODIFIED BY: {0}\n".format(m.__unicode__())
                mms = self.predecessors(m)
                if mms:
                    for ms in mms:
                        txt += "-"*8+"MODIFIED BY: {0}\n".format(ms.__unicode__())

        txt += u"_"*42+"\n"
        return txt
    def __str__(self):
        return self.__unicode__()#.encode('utf-8')
    def __repr__(self):
        return self.__unicode__()#.encode('utf-8')
    def getConTextModeNodes(self,mode):
        nodes = [n[0] for n in self.nodes(data=True) if n[1]['category'] == mode]
        nodes.sort()
        return nodes
    def updateScopes(self):
        """
        update the scopes of all the marked modifiers in the txt. The scope
        of a modifier is limited by its own span, the span of modifiers in the
        same category marked in the text, and modifiers with rule 'terminate'.
        """
        if self.getVerbose():
            print(u"updating scopes")
        self.__SCOPEUPDATED = True
        # make sure each tag has its own self-limited scope
        modifiers = self.getConTextModeNodes("modifier")
        for modifier in modifiers:
            if self.getVerbose():
                print(u"old scope for {0} is {1}".format(modifier.__str__(),modifier.getScope()))
            modifier.setScope()
            if self.getVerbose():
                print(u"new scope for {0} is {1}".format(modifier.__str__(),modifier.getScope()))


        # Now limit scope based on the domains of the spans of the other
        # modifier
        for i in range(len(modifiers)-1):
            modifier = modifiers[i]
            for j in range(i+1,len(modifiers)):
                modifier2 = modifiers[j]
                if modifier.limitScope(modifier2) and \
                   modifier2.getRule().lower() == 'terminate':
                    self.add_edge(modifier2,modifier)
                if modifier2.limitScope(modifier) and \
                   modifier.getRule().lower() == 'terminate':
                    self.add_edge(modifier,modifier2)

    def markItems(self,items, mode="target"):
        """tags the sentence for a list of items
        items: a list of contextItems"""
        if not items:
            return
        for item in items:
            self.add_nodes_from(self.markItem(item, ConTextMode=mode), category=mode)


    def markItem(self,item, ConTextMode="target", ignoreCase=True):
        """
        markup the current text with the current item.
        If ignoreCase is True (default), the regular expression is compiled with
        IGNORECASE."""

        if not self.getText():
            self.cleanText()

        # See if we have already created a regular expression

        if not item.getLiteral() in compiledRegExprs:
            if not item.getRE():
                regExp = r"\b{}\b".format(item.getLiteral())
                if self.getVerbose():
                    print("generating regular expression",regExp)
            else:
                regExp = item.getRE()
                if self.getVerbose():
                    print("using provided regular expression",regExp)
            if ignoreCase:
                r = re.compile(regExp, re.IGNORECASE|re.UNICODE)
            else:
                r = re.compile(regExp,re.UNICODE)
            compiledRegExprs[item.getLiteral()] = r
        else:
            r = compiledRegExprs[item.getLiteral()]
        iter = r.finditer(self.getText())
        terms=[]
        for i in iter:
            tO = tagObject(item,ConTextMode, tagid=self.getNextTagID(),
                           scope = self.getScope())

            tO.setSpan(i.span())
            tO.setPhrase(i.group())
            tO.setMatchedGroupDictionary(i.groupdict())
            if self.getVerbose():
                print(u"marked item",tO)
            terms.append(tO)
        return terms

    def pruneMarks(self):
        """
        prune Marked objects by deleting any objects that lie within the span of
        another object. Currently modifiers and targets are treated separately
        """
        self.__prune_marks(self.nodes(data=True))
    def dropInactiveModifiers(self):
        # if self.getVerbose():
        #     print("### in dropInactiveModifiers.")
        #     print("Raw:", self.getRawText())
        #     print(" All modifiers:")
        #     for n in self.getConTextModeNodes("modifier") :
        #         print(n,self.degree(n))
        #     print("All targets ({}):".format(self.getNumMarkedTargets()))
        #     for n in self.getMarkedTargets() :
        #         print(n)

        if self.getNumMarkedTargets() == 0:
            if self.getVerbose():
                print("No targets in this sentence; dropping ALL modifiers.")
            mnodes = self.getConTextModeNodes("modifier")
        else:
            mnodes = [ n for n in self.getConTextModeNodes("modifier") if self.degree(n) == 0]

        if self.getVerbose() and mnodes:
            print(u"dropping the following inactive modifiers")
            for mn in mnodes:
                print(mn)

        self.remove_nodes_from(mnodes)
    def pruneModifierRelationships(self):
        """Initially modifiers may be applied to multiple targets. This function
        computes the text difference between the modifier and each modified
        target and keeps only the minimum distance relationship

        Finally, we make sure that there are no self modifying modifiers present (e.g. "free" in
        the phrase "free air" modifying the target "free air").
        """
        modifiers = self.getConTextModeNodes("modifier")
        for m in modifiers:
            modifiedBy = self.successors(m)
            if modifiedBy and len(modifiedBy) > 1:
                minm = min([ (m.dist(mb),mb) for mb in modifiedBy ])
                edgs = self.edges(m)
                edgs.remove((m,minm[1]))
                if self.getVerbose():
                    print(u"deleting relationship(s)",edgs)

                self.remove_edges_from(edgs)

    def pruneSelfModifyingRelationships(self):
        """
        We make sure that there are no self modifying modifiers present (e.g. "free" in
        the phrase "free air" modifying the target "free air").
        modifiers = self.getConTextModeNodes("modifier")
        """
        modifiers = self.getConTextModeNodes("modifier")
        nodesToRemove = []
        for m in modifiers:
            modifiedBy = self.successors(m)
            if modifiedBy:
                for mb in modifiedBy:
                    if self.getVerbose():
                        print(mb,m,mb.encompasses(m))
                    if mb.encompasses(m):
                        nodesToRemove.append(m)
        if self.getVerbose():
            print("removing the following self modifying nodes",nodesToRemove)
        self.remove_nodes_from(nodesToRemove)
    def __prune_marks(self, marks):
        if len(marks) < 2:
            return
        # this can surely be done faster
        marks.sort()
        nodesToRemove = []
        for i in range(len(marks)-1):
            t1 = marks[i]
            if t1[0] not in nodesToRemove:
                for j in range(i+1,len(marks)):
                    t2 = marks[j]
                    if t1[0].encompasses(t2[0]) and t1[1]['category'] == t2[1]['category']:
                        nodesToRemove.append(t2[0])
                    elif t2[0].encompasses(t1[0]) and t2[1]['category'] == t1[1]['category']:
                        nodesToRemove.append(t1[0])
                        break
        if self.getVerbose():
            print(u"pruning the following nodes")
            for n in nodesToRemove:
                print(n)
        self.remove_nodes_from(nodesToRemove)

    def dropMarks(self,category="exclusion"):
        """Drop any targets that have the category equal to category"""
        if self.getVerbose():
            print("in dropMarks")
            for n in self.nodes():
                print(n.getCategory(),n.isA(category.lower()))
        dnodes = [n for n in self.nodes() if n.isA( category )]
        if self.getVerbose() and dnodes:
            print(u"droping the following markedItems")
            for n in dnodes:
                print(n)
        self.remove_nodes_from(dnodes)

    def applyModifiers(self):
        """
        If the scope has not yet been updated, do this first.

        Loop through the marked targets and for each target apply the modifiers
        """
        if not self.getScopeUpdated():
            self.updateScopes()
        targets = self.getConTextModeNodes("target")
        modifiers = self.getConTextModeNodes("modifier")
        for target in targets:
            for modifier in modifiers:
                if modifier.applyRule(target):
                    if self.getVerbose():
                        print(u"applying relationship between",modifier,target)

                    self.add_edge(modifier, target)
    def getMarkedTargets(self):
        """
        Return the list of marked targets in the current sentence. List is sorted by span
        """
        targets = self.getConTextModeNodes("target")
        targets.sort()
        return targets
    def getNumMarkedTargets(self):
        """
        Return the number of marked targets in the current sentence
        """
        return len(self.getConTextModeNodes("target"))

    def getModifiers(self, node):
        """
        return immediate predecessorts of node. The returned list is sorted by node span.
        """
        modifiers = self.predecessors(node)
        modifiers.sort()
        return modifiers
    def isModifiedByCategory(self,node, queryCategory):
        """
        tests whether node in markUp is modified by a tagObject with category equal to queryCategory. Return modifier if True
        """
        pred = self.getModifiers(node )
        for p in pred:
            if p.isA(queryCategory):
                return True

        return False

    def getTokenDistance(self,n1,n2):
        """returns the number of tokens (word) between n1 and n2"""
        txt = self.getText()
        if n1 < n2:
            start = n1.getSpan()[1]+1
            end = n2.getSpan()[0]
            direction = 1
        else:
            start = n2.getSpan()[1]+1
            end = n1.getSpan()[0]
            direction = -1

        subTxt = txt[start:end]
        tokens = subTxt.split()
        return len(tokens)*direction
