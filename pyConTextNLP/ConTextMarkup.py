"""
Module defining ConTextMarkup class
"""
import re
import uuid
from . io.xml import xmlScrub
from . tagObject import tagObject

import networkx as nx

REG_CLEAN1 = re.compile(r"""\W""", re.UNICODE)
REG_CLEAN2 = re.compile(r"""\s+""", re.UNICODE)
REG_CLEAN3 = re.compile(r"""\d""", re.UNICODE)

COMPILED_REGEXPRS = {}

NODE_XML_SKEL = \
"""
<node>
    {0}
</node>
"""

EDGE_XML_SKEL = \
"""
<edge>
    <startNode> {0} </startNode>
    <endNode> {1} </endNode>
    {2}
</edge>
"""

CONTEXT_MARKUP_XML_SKEL = \
"""
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


def create_tag_id():
    """
    get a unique identifier
    """
    return uuid.uuid1().int



class ConTextMarkup(nx.DiGraph):
    """
    base class for context document.
    build around markedTargets a list of termObjects representing desired terms
    found in text and markedModifiers, tagObjects found in the text
    """


    def __init__(self, txt='', unicodeEncoding='utf-8'):
        """txt is the string to parse"""
        # __document capture the document level structure
        # for each sentence and then put in the archives when the next sentence
        # is processed
        super(ConTextMarkup, self).__init__(__txt=None,
                                            __rawtxt=txt,
                                            __scope=None,
                                            __SCOPEUPDATED=False)
        self.__document = nx.DiGraph()
        self.__document.add_node("top", category="document")
        self.__VERBOSE = False
        self.__tagID = 0
        self.__unicodeEncoding = unicodeEncoding


    def getUnicodeEncoding(self):
        """
        return the unicode encoding used for the class
        """
        return self.__unicodeEncoding


    def toggleVerbose(self):
        """toggles the boolean value for verbose mode"""
        self.__VERBOSE = not self.__VERBOSE


    def getVerbose(self):
        """
        return the verbose setting
        """
        return self.__VERBOSE


    def setRawText(self, txt=''):
        """
        sets the current txt to txt and resets the current attributes to empty
        values, but does not modify the object archive
        """
        if self.getVerbose():
            print("Setting text to", txt)
        self.graph["__rawTxt"] = txt
        self.graph["__txt"] = None
        self.graph["__scope"] = None
        self.graph["__SCOPEUPDATED"] = False


    def getText(self):
        """
        return the cleaned text values
        """
        return self.graph.get("__txt", '')


    def getScope(self):
        """
        return the scope of the markup
        """
        return self.graph.get("__scope", '')


    def getScopeUpdated(self):
        """
        return boolean whether the scope has been updated
        """
        return self.graph.get("__SCOPEUPDATED")


    def getRawText(self):
        """
        get the original (uncleaned) text
        """
        return self.graph.get("__rawTxt", '')


    def getNumod_byerSentences(self): # !!! Need to rewrite this to match graph
        """
        get the numod_byer o sentences in the context
        """
        return len(self.__document)


    def cleanText(self, stripNonAlphaNumeric=False, stripNumod_byers=False):
        """Need to rename. applies the regular expression scrubbers to rawTxt"""
        if stripNonAlphaNumeric:
            txt = REG_CLEAN1.sub(" ", self.getRawText())
        else:
            txt = self.getRawText()

        # clean up white spaces
        txt = REG_CLEAN2.sub(" ", txt)
        if stripNumod_byers:
            txt = REG_CLEAN3.sub("", txt)

        self.graph["__scope"] = (0, len(txt))
        self.graph["__txt"] = txt
        if self.getVerbose():
            print("cleaned text is now", self.getText())


    def getXML(self):
        """
        return an XML representation of the markup
        """
        nodes = list(self.nodes(data=True))
        nodes.sort()
        node_string = ''
        for n in nodes:
            attribute_string = ''
            keys = list(n[1].keys())
            keys.sort()
            for k in keys:
                attribute_string += """<{0}> {1} </{2}>\n""".format(k, n[1][k], k)
            modification_string = ''
            modified_by = self.predecessors(n[0])
            if modified_by:
                for mod in modified_by:
                    modification_string += """<modified_by>\n"""
                    modification_string += \
                        """<modifyingNode> %s </modifyingNode>\n"""%mod.getTagID()
                    modification_string += \
                        """<modifyingCategory> %s </modifyingCategory>\n"""%mod.getCategory()
                    modification_string += """</modified_by>\n"""
            modifies = self.successors(n[0])
            if modifies:
                for modified in modifies:
                    modification_string += """<modifies>\n"""
                    modification_string += \
                        """<modifiedNode> {0} </modifiedNode>\n""".format(modified.getTagID())
                    modification_string += \
                        """</modifies>\n"""
            node_string += \
                    NODE_XML_SKEL.format(attribute_string+"{0}".format(n[0].getXML()) +\
                        modification_string)
        edges = list(self.edges(data=True))
        edges.sort()
        edge_string = ''
        for edge in edges:
            keys = list(edge[2].keys())
            keys.sort()
            attribute_string = ''
            for key in keys:
                attribute_string += """<{0}> {1} </{2}>\n""".format(key, edge[2][key], key)
            edge_string += "{0}".format(EDGE_XML_SKEL.format(edge[0].getTagID(),
                                                             edge[1].getTagID(),
                                                             attribute_string))

        return CONTEXT_MARKUP_XML_SKEL.format(xmlScrub(self.getRawText()),
                                              xmlScrub(self.getText()),
                                              node_string,
                                              edge_string)


    def __unicode__(self):
        txt = '_'*42+"\n"
        txt += 'rawText: {0}\n'.format(self.getRawText())
        txt += 'cleanedText: {0}\n'.format(self.getText())
        nodes = [n for n in self.nodes(data=True) if n[1].get('category', '') == 'target']
        nodes.sort()
        for n in nodes:
            txt += "*"*32+"\n"
            txt += "TARGET: {0}\n".format(n[0].__unicode__())
            modifiers = list(self.predecessors(n[0]))
            modifiers.sort()
            for mod in modifiers:
                txt += "-"*4+"MODIFIED BY: {0}\n".format(mod.__unicode__())
                modifiers = self.predecessors(mod)
                if modifiers:
                    for modifier in modifiers:
                        txt += "-"*8+"MODIFIED BY: %s\n"%modifier.__unicode__()

        txt += "_"*42+"\n"
        return txt


    def __str__(self):
        return self.__unicode__()
    def __repr__(self):
        return self.__unicode__()


    def getConTextModeNodes(self, mode):
        """
        get the numod_byer of nodes of type mode
        """
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
            print("updating scopes")
        self.__SCOPEUPDATED = True
        # make sure each tag has its own self-limited scope
        modifiers = self.getConTextModeNodes("modifier")
        for modifier in modifiers:
            if self.getVerbose():
                print("old scope for {0} is {1}".format(modifier.__str__(), modifier.getScope()))
            modifier.setScope()
            if self.getVerbose():
                print("new scope for {0} is {1}".format(modifier.__str__(), modifier.getScope()))


        # Now limit scope based on the domains of the spans of the other
        # modifier
        for i in range(len(modifiers)-1):
            modifier = modifiers[i]
            for j in range(i+1, len(modifiers)):
                modifier2 = modifiers[j]
                if modifier.limitScope(modifier2) and \
                   modifier2.getRule().lower() == 'terminate':
                    self.add_edge(modifier2, modifier)
                if modifier2.limitScope(modifier) and \
                   modifier.getRule().lower() == 'terminate':
                    self.add_edge(modifier, modifier2)


    def markItems(self, items, mode="target"):
        """tags the sentence for a list of items
        items: a list of contextItems"""
        if not items:
            return
        for item in items:
            self.add_nodes_from(self.markItem(item, ConTextMode=mode), category=mode)


    def markItem(self, item, ConTextMode="target", ignoreCase=True):
        """
        markup the current text with the current item.
        If ignoreCase is True (default), the regular expression is compiled with
        IGNORECASE."""

        if not self.getText():
            self.cleanText()

        # See if we have already created a regular expression

        if not item.getLiteral() in COMPILED_REGEXPRS:
            if not item.getRE():
                reg_exp = r"\b{}\b".format(item.getLiteral())
                if self.getVerbose():
                    print("generating regular expression", reg_exp)
            else:
                reg_exp = item.getRE()
                if self.getVerbose():
                    print("using provided regular expression", reg_exp)
            if ignoreCase:
                regex = re.compile(reg_exp, re.IGNORECASE|re.UNICODE)
            else:
                regex = re.compile(reg_exp, re.UNICODE)
            COMPILED_REGEXPRS[item.getLiteral()] = regex
        else:
            regex = COMPILED_REGEXPRS[item.getLiteral()]
        _iter = regex.finditer(self.getText())
        terms = []
        for i in _iter:
            tag_0 = tagObject(item,
                              ConTextMode,
                              tagid=create_tag_id(),
                              scope=self.getScope())

            tag_0.setSpan(i.span())
            tag_0.setPhrase(i.group())
            tag_0.setMatchedGroupDictionary(i.groupdict())
            if self.getVerbose():
                print("marked item", tag_0)
            terms.append(tag_0)
        return terms


    def pruneMarks(self):
        """
        prune Marked objects by deleting any objects that lie within the span of
        another object. Currently modifiers and targets are treated separately
        """
        self.__prune_marks(self.nodes(data=True))


    def dropInactiveModifiers(self):
        """
        drop modifiers that are not modifying any targets
        """
        if self.getNumMarkedTargets() == 0:
            if self.getVerbose():
                print("No targets in this sentence; dropping ALL modifiers.")
            mnodes = self.getConTextModeNodes("modifier")
        else:
            mnodes = [n for n in self.getConTextModeNodes("modifier") if self.degree(n) == 0]

        if self.getVerbose() and mnodes:
            print("dropping the following inactive modifiers")
            for node in mnodes:
                print(node)
        self.remove_nodes_from(mnodes)


    def pruneModifierRelationships(self):
        """Initially modifiers may be applied to multiple targets. This function
        computes the text difference between the modifier and each modified
        target and keeps only the minimum distance relationship

        Finally, we make sure that there are no self modifying modifiers present (e.g. "free" in
        the phrase "free air" modifying the target "free air").
        """
        modifiers = self.getConTextModeNodes("modifier")
        for modifier in modifiers:
            modified_by = self.successors(modifier)
            if modified_by and len(modified_by) > 1:
                minm = min([(modifier.dist(mod_by), mod_by) for mod_by in modified_by])
                edgs = self.edges(modifier)
                edgs.remove((modifier, minm[1]))
                if self.getVerbose():
                    print("deleting relationship(s)", edgs)

                self.remove_edges_from(edgs)


    def pruneSelfModifyingRelationships(self):
        """
        We make sure that there are no self modifying modifiers present (e.g. "free" in
        the phrase "free air" modifying the target "free air").
        modifiers = self.getConTextModeNodes("modifier")
        """
        modifiers = self.getConTextModeNodes("modifier")
        nodes_to_remove = []
        for modifier in modifiers:
            modified_by = self.successors(modifier)
            if modified_by:
                for mod_by in modified_by:
                    if self.getVerbose():
                        print(mod_by, modifier, mod_by.encompasses(modifier))
                    if mod_by.encompasses(modifier):
                        nodes_to_remove.append(modifier)
        if self.getVerbose():
            print("removing the following self modifying nodes", nodes_to_remove)
        self.remove_nodes_from(nodes_to_remove)


    def __prune_marks(self, _marks):
        if len(_marks) < 2:
            return
        # this can surely be done faster
        marks = list(_marks)
        marks.sort()
        nodes_to_remove = []
        for i in range(len(marks)-1):
            mark1 = marks[i]
            if mark1[0] not in nodes_to_remove:
                for j in range(i+1, len(marks)):
                    mark2 = marks[j]
                    if mark1[0].encompasses(mark2[0]) and \
                       mark1[1]['category'] == mark2[1]['category']:
                        nodes_to_remove.append(mark2[0])
                    elif mark2[0].encompasses(mark1[0]) and \
                         mark2[1]['category'] == mark1[1]['category']:
                        nodes_to_remove.append(mark1[0])
                        break
        if self.getVerbose():
            print("pruning the following nodes")
            for node in nodes_to_remove:
                print(node)
        self.remove_nodes_from(nodes_to_remove)


    def dropMarks(self, category="exclusion"):
        """Drop any targets that have the category equal to category"""
        if self.getVerbose():
            print("in dropMarks")
            for n in self.nodes():
                print(n.getCategory(), n.isA(category.lower()))
        dnodes = [n for n in self.nodes() if n.isA(category)]
        if self.getVerbose() and dnodes:
            print("droping the following markedItems")
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
                        print("applying relationship between", modifier, target)

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
        Return the numod_byer of marked targets in the current sentence
        """
        return len(self.getConTextModeNodes("target"))


    def getModifiers(self, node):
        """
        return immediate predecessorts of node. The returned list is sorted by node span.
        """
        modifiers = self.predecessors(node)
        modifiers.sort()
        return modifiers


    def isModifiedByCategory(self, node, queryCategory):
        """
        tests whether node in markUp is modified by a tagObject
        with category equal to queryCategory.  Return modifier if True
        """
        predecessors = self.getModifiers(node)
        for predecessor in predecessors:
            if predecessor.isA(queryCategory):
                return True

        return False


    def getTokenDistance(self, node1, node2):
        """returns the numod_byer of tokens (word) between node1 and node2"""
        txt = self.getText()
        if node1 < node2:
            start = node1.getSpan()[1]+1
            end = node2.getSpan()[0]
            direction = 1
        else:
            start = node2.getSpan()[1]+1
            end = node1.getSpan()[0]
            direction = -1

        sub_txt = txt[start:end]
        tokens = sub_txt.split()
        return len(tokens)*direction
