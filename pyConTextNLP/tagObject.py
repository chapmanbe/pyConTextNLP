"""
tabObject module
"""

import uuid
import copy
from .io.xml import xmlScrub

tagObjectXMLSkel=\
"""
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


class tagObject(object):
    """
    A class that describes terms of interest in the text.
    tagObject is characterized by the following attributes
    1) The contextItem defining the tag
    3) The location of the tag within the text being parsed

    """
    def __init__(self, item, ConTextCategory, scope=None, tagid=None, **kwargs):
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


    def limitScope(self, obj):
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


    def applyRule(self, term):
        """applies self's rule to term. If the start of term lines within
        the span of self, then term may be modified by self"""
        if not self.getRule() or self.getRule() == 'terminate':
            return False
        if self.__scope[0] <= term.getSpan()[0] <= self.__scope[1]:
            return True 


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


    def replaceCategory(self,oldCategory, newCategory):
        for index, item in enumerate(self.__category):
            if item == oldCategory.lower().strip():
                try:
                    self.__category[index] = newCategory.lower().strip()
                except:
                    del self.__category[index]
                    self.__category.extend([nc.lower().strip() for nc in newCategory])


    def setSpan(self, span):
        """set the span within the associated text for this object"""
        self.__spanStart = span[0]
        self.__spanEnd = span[1]


    def getSpan(self):
        """return the span within the associated text for this object"""
        return self.__spanStart,self.__spanEnd

    def setPhrase(self, phrase):
        """set the actual matched phrase used to generate this object"""
        self.__foundPhrase = phrase


    def getPhrase(self):
        """return the actual matched phrase used to generate this object"""
        return self.__foundPhrase


    def setMatchedGroupDictionary(self, mdict):
        """set the foundDict variable to mdict. This gets the name/value pair for each NAMED group within the regular expression"""
        self.__foundDict = mdict.copy()


    def getMatchedGroupDictionary(self):
        """return a copy of the matched group dictionary"""
        return self.__foundDict.copy()


    def dist(self, obj):
        """returns the minimum distance from the current object and obj.
        Distance is measured as current start to object end or current end to object start"""
        return min(abs(self.__spanEnd-obj.__spanStart), abs(self.__spanStart-obj.__spanEnd))

    def __lt__(self, other): return self.__spanStart < other.__spanStart
    def __le__(self, other): return self.__spanStart <= other.__spanStart
    def __eq__(self, other):
        return (self.__spanStart == other.__spanStart and
                self.__spanEnd == other.__spanEnd)
    def __ne__(self, other): return self.__spanStart != other.__spanStart
    def __gt__(self, other): return self.__spanStart > other.__spanStart
    def __ge__(self, other): return self.__spanStart >= other.__spanStart

    def __hash__(self):
        return hash(repr(self))


    def encompasses(self, other):
        """tests whether other is completely encompassed with the current object
           ??? should we not prune identical span tagObjects???"""
        if self.__spanStart <= other.__spanStart and \
           self.__spanEnd >= other.__spanEnd:
            return True
        else:
             return False


    def overlap(self, other):
        """
        tests whether other overlaps with self
        """
        if (other.__spanStart >= self.__spanStart and other.__spanStart <= self.__spanEnd ) or \
           (other.__spanEnd >= self.__spanStart and other.__spanEnd <= self.__spanEnd):
            return True
        else:
            return False


    def leftOverlap(self, other):
        """
        tests whether other has partial overlap to the left with self.
        """
        if self.encompasses(other):
            return False
        if self.overlap(other) and self.__gt__(other):
            return True
        else:
            return False


    def rightOverlap(self, other):
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
        return self.__unicode__()
    def __repr__(self):
        return self.__unicode__()



