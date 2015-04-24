import re
import networkx as nx

from tagObjects import tagObject
import tagObjects as TO

r1 = re.compile(r"""\W""",re.UNICODE)
r2 = re.compile(r"""\s+""",re.UNICODE)
r3 = re.compile(r"""\d""",re.UNICODE)

rlt = re.compile(r"""<""",re.UNICODE)
ramp = re.compile(r"""&""",re.UNICODE)

compiledRegExprs = {}
ConTextMarkupXMLSkel = u"""
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
edgeXMLSkel=u"""
<edge>
<startNode> %s </startNode>
<endNode> %s </endNode>
%s
</edge>
"""
nodeXMLSkel=u"""
<node>
%s
</node>
"""

def modifyforward(tag1,tag2):
    pass



def setRawText(markup,txt=u''):
    """
    sets the current txt to txt and resets the current attributes to empty
    values, but does not modify the object archive
    """
    markupNew = markup.copy() 
    if( markupNew.getVerbose() ):
        print "Setting text to",txt
    markupNew.graph["__rawTxt"] = txt
    markupNew.graph["__txt"] = None
    markupNew.graph["__scope"] = None
    markupNew.graph["__SCOPEUPDATED"] = False
    return markupNew



def cleanText(markup,stripNonAlphaNumeric=False, stripNumbers=False):
    """Need to rename. applies the regular expression scrubbers to rawTxt"""
    markupNew = markup.copy()
    if( stripNonAlphaNumeric ):
        txt = r1.sub(" ",markupNew.getRawText() )
    else:
        txt = markupNew.getRawText()

    # clean up white spaces
    txt = r2.sub(" ",txt)
    if( stripNumbers ):
        txt = r3.sub("",txt)

    markupNew.graph["__txt"] = txt
    if( markupNew.getVerbose() ):
        print u"cleaned text is now",markupNew.getText()
    return markupNew



def updateScopes(markup):
    """
    update the scopes of all the marked modifiers in the txt. The scope
    of a modifier is limited by its own span, the span of modifiers in the
    same category marked in the text, and modifiers with rule 'terminate'.
    """
    markupNew = markup.copy()
    if markupNew.getVerbose():
        print u"updating scopes"
    modifiers = markupNew.getConTextModeNodes("modifier")
    for modifier in modifiers:
        if(markupNew.getVerbose()):
            print(u"old scope for %s is %s"%(modifier.__str__(),modifier.getScope()))
            modifier.setScope()
        if(markupNew.getVerbose()):
            print(u"new scope for %s is %s"%(modifier.__str__(),modifier.getScope()))


    # Now limit scope based on the domains of the spans of the other
    # modifier
    for i in range(len(modifiers)-1):
        modifier = modifiers[i]
        for j in range(i+1,len(modifiers)):
            modifier2 = modifiers[j]
            if( TO.limitScope(modifier,modifier2) and
                    modifier2.ti.citem.getRule().lower() == 'terminate'):
                markupNew.add_edge(modifier2,modifier)
            if( TO.limitScope(modifier2,modifier) and
                    modifier.ti.citem.getRule().lower() == 'terminate'):
                markupNew.add_edge(modifier,modifier2)
    markupNew.graph["__SCOPEUPDATED"] = True
    return markupNew



def pruneMarks(markup):
    """
    prune Marked objects by deleting any objects that lie within the span of
    another object. Currently modifiers and targets are treated separately
    """
    markupNew = markup.copy()

    marks = markupNew.nodes(data=True)
    if( len(marks) < 2 ):
        return markupNew
    marks.sort()
    nodesToRemove = []
    for i in range(len(marks)-1):
        if( marks[i][0] not in nodesToRemove ):
            for j in range(i+1,len(marks)):
                if( TO.encompasses(marks[i][0],marks[j][0]) and marks[i][1]['category'] == marks[j][1]['category'] ):
                    nodesToRemove.append(marks[j][0])
                elif( TO.encompasses(marks[j][0],marks[i][0]) and marks[i][1]['category'] == marks[j][1]['category'] ):
                    nodesToRemove.append(marks[i][0])
                    break
    if( markupNew.getVerbose() ):
        print u"pruning the following nodes"
        for n in nodesToRemove:
            print n
    markupNew.remove_nodes_from(nodesToRemove)
    return markupNew



def markItem(markup,item, ConTextMode="target", ignoreCase=True):
    """
    markup the current text with the current item.
    If ignoreCase is True (default), the regular expression is compiled with
    IGNORECASE."""


    if not compiledRegExprs.has_key(item.getLiteral()):
        if(not item.getRE()):
            regExp = ur"\b%s\b"%item.getLiteral()
        else:
            regExp = item.getRE()
        if ignoreCase:
            r = re.compile(regExp, re.IGNORECASE|re.UNICODE)
        else:
            r = re.compile(regExp,re.UNICODE)
        compiledRegExprs[item.getLiteral()] = r
    else:
        r = compiledRegExprs[item.getLiteral()]
    miter = r.finditer(markup.getText())
    terms=[]
    for i in miter:
        # ci, span, scope,foundPhrase,ConTextCategory,tagid
        tO = tagObject(item,i.span(),markup.getScope(),i.group(),ConTextMode, markup.getNextTagID())

        terms.append(tO)
    return terms



def markItems(markup,items, mode="target"):
    """tags the sentence for a list of items
    items: a list of contextItems"""
    # ??? Why am I adding mode to both the tag object and the markup node graph??? 
    markupNew = markup.copy()
    if( not items ):
        return markupNew
    for item in items:
        markupNew.add_nodes_from(markItem(markupNew,item, ConTextMode=mode), category=mode)
    return markupNew



def keepClosestMarkupRelationships(markup):
    """Initially modifiers may be applied to multiple targets. This function
    computes the text difference between the modifier and each modified
    target and keeps only the minimum distance relationship

    Finally, we make sure that there are no self modifying modifiers present (e.g. "free" in 
    the phrase "free air" modifying the target "free air").
    """
    markupNew = markup.copy()
    modifiers = markupNew.getConTextModeNodes("modifier")
    for m in modifiers:
        modifiedBy = markupNew.successors(m)
        if( modifiedBy and len(modifiedBy) > 1 ):
            minm = min([ (m.dist(mb),mb) for mb in modifiedBy ])
            edgs = self.edges(m)
            edgs.remove((m,minm[1]))
            if( self.getVerbose() ):
                print u"deleting relationship(s)",edgs

            self.remove_edges_from(edgs)



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

    return ConTextMarkupXMLSkel%(xmlScrub(self.getRawText()),xmlScrub(self.getText()),
                                   nodeString,edgeString)



def getConTextModeNodes(markup,mode):
    nodes = [n[0] for n in markup.nodes(data=True) if n[1]['category'] == mode]
    nodes.sort()
    return nodes



def getMarkedTargets(markup):
    """
    Return the list of marked targets in the current sentence. List is sorted by span
    """
    targets = markup.getConTextModeNodes("target")
    targets.sort()
    return targets



def getTokenDistance(markup,n1,n2):
    """returns the number of tokens (word) between n1 and n2"""
    txt = markup.getText()
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



def applyModifiers(markup):
    """
    If the scope has not yet been updated, do this first.

    Loop through the marked targets and for each target apply the modifiers
    """
    if( not markup.getScopeUpdated() ):
        markupNew = updateScopes(markup)
    else:
        markupNew = markup.copy()
    targets = markupNew.getConTextModeNodes("target")
    modifiers = markupNew.getConTextModeNodes("modifier")
    for target in targets:
        for modifier in modifiers:
            if( TO.applyRule(modifier,target) ):
                if( markupNew.getVerbose() ):
                    print u"applying relationship between",modifier,target
                markupNew.add_edge(modifier, target)
    return markupNew



def dropMarks(markup, category="exclusion"):
    """Drop any targets that have the category equal to category"""
    markupNew = markup.copy()
    dnodes = [n for n in markupNew.nodes() if n.isA( category )]
    markupNew.remove_nodes_from(dnodes)
    return markupNew



def pruneSelfModifyingRelationships(markup):
    """
    We make sure that there are no self modifying modifiers present (e.g. "free" in 
    the phrase "free air" modifying the target "free air").
    modifiers = self.getConTextModeNodes("modifier")
    """
    markupNew = markup.copy()
    modifiers = markup.getConTextModeNodes("modifier")
    nodesToRemove = []
    for m in modifiers:
        modifiedBy = markup.successors(m)
        if( modifiedBy ):
            for mb in modifiedBy:
                if( TO.encompasses(mb,m) ):
                    nodesToRemove.append(m)
    markupNew.remove_nodes_from(nodesToRemove)
    return markupNew



class ConTextMarkup(nx.DiGraph):
    """
    base class for context document.
    build around markedTargets a list of termObjects representing desired terms
    found in text and markedModifiers, tagObjects found in the text
    """
    def __init__(self,txt=u'',unicodeEncoding='utf-8',verbose=False,tagID=0):
        """txt is the string to parse"""
        # __document capture the document level structure
        # for each sentence and then put in the archives when the next sentence
        # is processed
        super(ConTextMarkup,self).__init__(__txt=None,__rawTxt=txt,
                                           __SCOPEUPDATED=False,__VERBOSE=verbose,
                                           __tagID=tagID,
                                           __unicodeEncoding=unicodeEncoding)
        self.__cleanText()

    def __cleanText(self,stripNonAlphaNumeric=False, stripNumbers=False):
        """Need to rename. applies the regular expression scrubbers to rawTxt"""
        if stripNonAlphaNumeric:
            txt = r1.sub(" ",self.getRawText() )
        else:
            txt = self.getRawText()
        # clean up white spaces
        txt = r2.sub(" ",txt)
        if stripNumbers:
            txt = r3.sub("",txt)
        self.graph["__txt"] = txt
        self.graph["__scope"] = (0,len(txt))

    def getUnicodeEncoding(self):
        return self.graph["__unicodeEncoding"]

    def getNextTagID(self):
        """???"""
        self.graph["__tagID"] += 1
        return u"cid%02d"%self.graph["__tagID"]

    def getVerbose(self):
        return self.graph["__VERBOSE"]
    def getText(self):
        return self.graph.get("__txt",u'')
    def getScope(self):
        return self.graph.get("__scope",u'')
    def getScopeUpdated(self):
        return self.graph.get("__SCOPEUPDATED")
    def getRawText(self):
        return self.graph.get("__rawTxt",u'')
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
            #if( queryCategory.lower() == p.getCategory().lower() ):
            if( p.isA(queryCategory) ):
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

