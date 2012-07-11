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

r1 = re.compile(r"""\W""",re.UNICODE)
r2 = re.compile(r"""\s+""",re.UNICODE)
r3 = re.compile(r"""\d""",re.UNICODE)

compiledRegExprs = {}

        
tagObjectXMLSkel=\
u"""
<tagObject>
<id> %s </id>
<phrase> %s </phrase>
<literal> %s </literal>
<category> %s </category>
<spanStart> %d </spanStart>
<spanStop> %d </spanStop>
<scopeStart> %d </scopeStart>
<scopeStop> %d </scopeStop>
</tagObject>
"""

ConTextMarkupXMLSkel = \
u"""
<ConTextMarkup>
<rawText> %s </rawText>
<cleanText> %s </cleanText>
<nodes>
%s
</nodes>
<edges>
%s
</edges>
</ConTextMarkup>
"""
edgeXMLSkel=\
u"""
<edge>
<startNode> %s </startNode>
<endNode> %s </endNode>
%s
</edge>
"""
nodeXMLSkel=\
u"""
<node>
%s
</node>
"""

ConTextDocumentXMLSkel=\
u"""
<ConTextDocument>
%s
</ConTextDocument>
"""
class tagObject(object):
    """
    A class that describes terms of interest in the text.
    tagObject is characterized by the following attributes
    1) The contextItem defining the tag
    3) The location of the tag within the text being parsed

    """
    def __init__(self, item, ConTextCategory,scope=None, tagid='', **kwargs):
        """
        item: contextItem used to generate term
        ConTextCategory: category this term is being used for in pyConText
        
        variants
        """
        self.__item = item
        self.__spanStart = 0
        self.__spanEnd = 0
        self.__ConTextCategory = ConTextCategory
        self.__tagID = tagid
        if( scope == None ):
            self.__scope = []
        else:
            self.__scope = list(scope)
        self.__SCOPEUPDATED = False
    def setScope(self):
        """
        applies the objects own rule and span to modify the object's scope
        Currently only "forward" and "backward" rules are implemented
        """
        
        if( 'forward' in self.__item.getRule().lower() ):
            self.__scope[0] = self.getSpan()[1]
        elif( 'backward' in self.__item.getRule().lower() ):
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
        if( not self.getRule() or self.getRule()== 'terminate' or 
             (self.getCategory() != obj.getCategory() and obj.getRule() != 'terminate')):
            return False
        originalScope = copy.copy((self.getScope()))
        if( 'forward' in self.getRule().lower() or 
            'bidirectional' in self.getRule().lower() ):
            if( obj > self ):
                self.__scope[1] = min(self.__scope[1],obj.getSpan()[0])
        elif( 'backward' in self.getRule().lower() or 
              'bidirectional' in self.getRule().lower() ):
            if( obj < self ):
                self.__scope[0] = max(self.__scope[0],obj.getSpan()[1])
        if( originalScope != self.__scope ):
            return True
        else:
            return False
        
    def applyRule(self,term):
        """applies self's rule to term. If the start of term lines within
        the span of self, then term may be modified by self"""
        if( not self.getRule() or self.getRule() == 'terminate'):
            return False
        if(self.__scope[0] <= term.getSpan()[0] <= self.__scope[1]):
            return True #term.updateModifiedBy(self)
    def getConTextCategory(self):
        return self.__ConTextCategory
    def getXML(self):
        return   tagObjectXMLSkel%(self.getTagID(),self.getPhrase(),self.getLiteral(),self.getCategory(),
                                    self.getSpan()[0],self.getSpan()[1],
                                    self.getScope()[0],self.getScope()[1])

    def getBriefDescription(self):
        description = u"""<id> %s </id> """%self.getTagID()
        description+= u"""<phrase> %s </phrase> """%self.getPhrase()
        description+= u"""<category> %s </category> """%self.getCategory()
        return description
    def getLiteral(self):
        """returns the term defining this object"""
        return self.__item.getLiteral()
    def getCategory(self):
        """returns the category (e.g. CONJUNCTION) for this object"""
        return self.__item.getCategory()
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
    def encompasses(self,other):
        """tests whether other is completely encompassed with the current object
           ??? should we not prune identical span tagObjects???"""
        if( self.__spanStart <= other.__spanStart and 
            self.__spanEnd >= other.__spanEnd ):
            return True
        else:
             return False
    def __unicode__(self):
        txt = self.getBriefDescription()
        return txt
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __repr__(self):
        return unicode(self).encode('utf-8')
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
        if( setToParent ):
            self.__currentParent = self.__document.node(sectionLabel)

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
        if( edge ):
            return edge[0]

    def getSectionNodes(self,sectionLabel = None, category="markup"):
        if( not sectionLabel ):
            sectionLabel = self.__currentParent
        successors = [(e[2]['__sectionNumber'],e[1]) for e in self.__document.out_edges(sectionLabel, data=True) 
                                                            if e[2].get("category") == category]
        successors.sort()
        tmp = zip(*successors)
        return tmp[1]

    def getSectionMarkups(self, sectionLabel = None, returnSentenceNumbers=True ):
        """return the markup graphs for the section ordered by sentence number"""
        if( not sectionLabel ):
            sectionLabel = self.__currentParent
        successors = [(e[2]['sentenceNumber'],e[1]) for e in self.__document.out_edges(sectionLabel, data=True) 
                                                            if e[2].get("category") == "markup"]
        successors.sort()
        if( returnSentenceNumbers ):
            return successors
        else:
            tmp = zip(*successors)
            return tmp[1]

    def getDocumentSections(self):
        edges = [ (e[2]['sectionNumber'],e[1]) for e in self.__document.edges(data=True) if e[2].get("category") == "section"]
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
        if( not self.__documentGraph ):
            self.computeDocumentGraph()
        return self.__documentGraph

    def getXML(self):
        txt = u""

        # get children sections of root
        
        sections = self.getDocumentSections()
        for s in sections:
            txt += u"""<section>\n<sectionLabel> %s </sectionLabel>\n"""%s
            markups = self.getSectionMarkups(s)
            for m in markups:
                txt += u"<sentence>\n<sentenceNumber> %s </sentenceNumber>\n</sentence>\n%s"%(m[0],m[1].getXML())
            txt += u"""</section>\n"""

        return ConTextDocumentXMLSkel%txt
    def __unicode__(self):
        txt = u'_'*42+"\n"
        return txt
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __repr__(self):
        return unicode(self).encode('utf-8')
    def getConTextModeNodes(self,mode):
        """
        Deprecated. This functionality should be accessed via the ConTextMarkup object now returned from getDocumentGraph()
        """
        print "This function is deprecated and will be eliminated shortly."
        print "The same functionality can be accessed through the ConTextMarkup object returned from getDocumentGraph()"
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
        if( verbose ):
            print "Document markup has %d edges"%self.__document.number_of_edges()
        markups = [e[1] for e in self.__document.edges(data=True) if e[2].get('category') == 'markup']
        if( verbose ):
            print "Document markup has %d conTextMarkup objects"%len(markups)
        ic = 0
        for i in range(len(markups)):
        #for m in markups:
            m = markups[i]
            if( verbose ):
                print "markup %d has %d total items including %d targets"%(i,m.number_of_nodes(),m.getNumMarkedTargets())

            self.__documentGraph = nx.union(m,self.__documentGraph)
            if( verbose ):
                print "documentGraph now has %d nodes"%self.__documentGraph.number_of_nodes()

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
        self.__tagID += 1
        return u"cid%06d"%self.__tagID
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
	if( self.getVerbose() ):
	    print "Setting text to",txt
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
        if( stripNonAlphaNumeric ):
            txt = r1.sub(" ",self.getRawText() )
        else:
            txt = self.getRawText()

        # clean up white spaces
        txt = r2.sub(" ",txt)
        if( stripNumbers ):
            txt = r3.sub("",txt)
           
        self.graph["__scope"] = (0,len(txt))
        self.graph["__txt"] = txt
	if( self.getVerbose() ):
	    print u"cleaned text is now",self.getText()
    def getXML(self):
        nodes = self.nodes(data=True) 
        nodes.sort()
        nodeString = u''
        for n in nodes:
            attributeString = u''
            keys = n[1].keys()
            keys.sort()
            for k in keys:
                attributeString += """<%s> %s </%s>\n"""%(k,n[1][k],k)
            modificationString = u'' 
            modifiedBy = self.predecessors(n[0])
            if( modifiedBy ):
                for m in modifiedBy:
                    modificationString += u"""<modifiedBy>\n"""
                    modificationString += u"""<modifyingNode> %s </modifyingNode>\n"""%m.getTagID()
                    modificationString += u"""<modifyingCategory> %s </modifyingCategory>\n"""%m.getCategory()
                    modificationString += u"""</modifiedBy>\n"""
            modifies = self.successors(n[0])
            if( modifies ):
                for m in modifies:
                    modificationString += u"""<modifies>\n"""
                    modificationString += u"""<modifiedNode> %s </modifiedNode>\n"""%m.getTagID()
                    modificationString += u"""</modifies>\n"""
            nodeString += nodeXMLSkel%(attributeString+"%s"%n[0].getXML()+modificationString )
        edges = self.edges(data=True)
        edges.sort()
        edgeString = u''
        for e in edges:
            keys = e[2].keys()
            keys.sort()
            attributeString = u''
            for k in keys:
                attributeString += """<%s> %s </%s>\n"""%(k,e[2][k],k)
            edgeString += "%s"%edgeXMLSkel%(e[0].getTagID(),e[1].getTagID(),attributeString)

        return ConTextMarkupXMLSkel%(self.getRawText(),self.getText(),
                                       u"%s"%nodeString,u"%s"%edgeString)
    def __unicode__(self):
        txt = u'_'*42+"\n"
	txt += 'rawText: %s\n'%self.getRawText()
	txt += 'cleanedText: %s\n'%self.getText()
	nodes = [n for n in self.nodes(data=True) if n[1].get('category','') == 'target']
        nodes.sort()
	for n in nodes:
	    txt += "*"*32+"\n"
	    txt += "TARGET: %s\n"%n[0].__unicode__()
	    modifiers = self.predecessors(n[0])
            modifiers.sort()
	    for m in modifiers:
	        txt += "-"*4+"MODIFIED BY: %s\n"%m.__unicode__()
                mms = self.predecessors(m)
                if( mms ):
                    for ms in mms:
                        txt += "-"*8+"MODIFIED BY: %s\n"%ms.__unicode__()
	    
        txt += u"_"*42+"\n"
        return txt
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __repr__(self):
        return unicode(self).encode('utf-8')
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
	if( self.getVerbose() ):
	    print u"updating scopes"
        self.__SCOPEUPDATED = True
        # make sure each tag has its own self-limited scope
        modifiers = self.getConTextModeNodes("modifier")
        for modifier in modifiers:
	    if(self.getVerbose()):
	        print u"old scope for %s is %s"%(modifier.__str__(),modifier.getScope())
            modifier.setScope()
	    if(self.getVerbose()):
	        print u"new scope for %s is %s"%(modifier.__str__(),modifier.getScope())


        # Now limit scope based on the domains of the spans of the other
        # modifier
        for i in range(len(modifiers)-1):
            modifier = modifiers[i]
            for j in range(i+1,len(modifiers)):
                modifier2 = modifiers[j]
                if( modifier.limitScope(modifier2) and 
                        modifier2.getRule().lower() == 'terminate'):
                    self.add_edge(modifier2,modifier)
                if( modifier2.limitScope(modifier) and 
                        modifier.getRule().lower() == 'terminate'):
                    self.add_edge(modifier,modifier2)

    def markItems(self,items, mode="target"):
        """tags the sentence for a list of items
        items: a list of contextItems"""
        if( not items ):
            return
        for item in items:
            self.add_nodes_from(self.markItem(item, ConTextMode=mode), category=mode)

                                
    def markItem(self,item, ConTextMode="target", ignoreCase=True ):
        """
        markup the current text with the current item.
        If ignoreCase is True (default), the regular expression is compiled with
        IGNORECASE."""
            
        if( not self.getText() ):
            self.cleanText()

        # See if we have already created a regular expression

        if(not compiledRegExprs.has_key(item.getLiteral()) ):
            if(not item.getRE()):
                regExp = item.getLiteral()
            else:
                regExp = item.getRE()
            if( ignoreCase ):
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
            if( self.getVerbose() ):
                print u"marked item",tO
            terms.append(tO)
        return terms

    def pruneMarks(self):    
        """
        prune Marked objects by deleting any objects that lie within the span of
        another object. Currently modifiers and targets are treated separately
        """
        self.__prune_marks(self.nodes())
    def dropInactiveModifiers(self):
        mnodes = [ n for n in self.getConTextModeNodes("modifier") if self.degree(n) == 0]
        if( self.getVerbose() and mnodes ):
            print u"dropping the following inactive modifiers"
            for mn in mnodes:
                print mn

        self.remove_nodes_from(mnodes)
    def pruneModifierRelationships(self):
        """Initially modifiers may be applied to multiple targets. This function
        computes the text difference between the modifier and each modified
        target and keeps only the minimum distance relationship"""
        modifiers = self.getConTextModeNodes("modifier")
        for m in modifiers:
            modifiedBy = self.successors(m)
            if( modifiedBy and len(modifiedBy) > 1 ):
                minm = min([ (m.dist(mb),mb) for mb in modifiedBy ])
                edgs = self.edges(m)
                if( self.getVerbose() ):
                    print u"deleting relationship",m,minm[1]
                edgs.remove((m,minm[1]))
                self.remove_edges_from(edgs)
        
    def __prune_marks(self, marks):
        if( len(marks) < 2 ):
            return
        # this can surely be done faster
        marks.sort()
        nodesToRemove = []
        for i in range(len(marks)-1):
            t1 = marks[i]
            if( t1 not in nodesToRemove ):
                for j in range(i+1,len(marks)):
                    t2 = marks[j]
                    if( t1.encompasses(t2) ):
                        nodesToRemove.append(t2)
                    elif( t2.encompasses(t1) ):
                        nodesToRemove.append(t1)
                        break
        if( self.getVerbose() ):
            print u"pruning the following nodes"
            for n in nodesToRemove:
                print n
        self.remove_nodes_from(nodesToRemove)
        
    def dropMarks(self,category="exclusion"):
        """Drop any targets that have the category equal to category"""
        dnodes = [n for n in self.nodes() if n.getCategory().lower() == category.lower()]
        if( self.getVerbose() and dnodes ):
            print u"droping the following markedItems"
            for n in dnodes:
                print n
        self.remove_nodes_from(dnodes)           

    def applyModifiers(self):
        """
        If the scope has not yet been updated, do this first.
        
        Loop through the marked targets and for each target apply the modifiers
        """
        if( not self.getScopeUpdated() ):
            self.updateScopes()
        targets = self.getConTextModeNodes("target")
        modifiers = self.getConTextModeNodes("modifier")
        for target in targets:
            for modifier in modifiers:
                if( modifier.applyRule(target) ):
                    if( self.getVerbose() ):
                        print u"applying relationship between",modifier,target

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
            if( queryCategory.lower() == p.getCategory().lower() ):
                return True
                 
        return False
    def isModifiedBy(self, node, query):
        """
        Tests whether node in markUp is modified by any tagObjects with category including query. This does not need to be an exact match. Thus "probable" will match "probable_existence" and "probable_negated_existence"
        """
        pred = self.getModifiers(node)
        q = query.lower()
        for p in pred:
            if( q in p.getCategory().lower() ):
                return True
        return False

    def getTokenDistance(self,n1,n2):
        """returns the number of tokens (word) between n1 and n2"""
        txt = self.getText()
        if( n1 < n2 ):
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
