import collections
from ConTextItem import ConTextItem

from utils import xmlScrub




tagObjectXMLSkel=u"""
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


titem = collections.namedtuple('titem', ['citem', 'span','scope','foundPhrase','ConTextCategory','id'])

def limitCategoryScopeForward(obj1,obj2):
    """If obj1 and obj2 are of the same category
    modify the scope of 
    """
    objNew = obj1.copy()
    if not objNew.isA(obj2.ti.citem.getCategory()):
        return objNew
    if obj2 > objNew:
        objNew.ti.scope[1] = min(objNew.ti.scope[1],obj2.getSpan()[0])
    return objNew


def limitCategoryScopeBackward(obj1,obj2):
    """If obj1 and obj2 are of the same category
    modify the scope of 
    """
    objNew = obj1.copy()
    if not objNew.isA(obj2.ti.citem.getCategory()):
        return objNew
    if obj2 < objNew:
            objNew.ti.scope[0] = max(objNew.ti.scope[0],obj2.getSpan()[1])
    return objNew


def limitCategoryScopeBidirectional(obj1,obj2):
    """If obj1 and obj2 are of the same category
    modify the scope of 
    """
    objNew = obj1.copy()
    if not objNew.isA(obj2.ti.citem.getCategory()):
        return objNew
    if obj2 > objNew:
        objNew.ti.scope[1] = min(objNew.ti.scope[1],obj2.getSpan()[0])
    if obj2 < objNew:
            objNew.ti.scope[0] = max(objNew.ti.scope[0],obj2.getSpan()[1])
    return objNew


def limitScope(obj1,obj2):
    """If obj1 and obj2 are of the same category or if obj2 has a rule of
    'terminate', use the span of obj2 to
    update the scope of obj1
    """
    objNew = obj1.copy()
    if( not objNew.ti.citem.getRule() or objNew.ti.citem.getRule()== 'terminate' or
         (not objNew.isA(obj2.ti.citem.getCategory()) and obj2.ti.citem.getRule() != 'terminate')):
        return objNew
    if( 'forward' in objNew.ti.citem.getRule().lower() or
        'bidirectional' in objNew.ti.citem.getRule().lower() ):
        if( obj2 > objNew ):
            objNew.ti.scope[1] = min(objNew.ti.scope[1],obj2.getSpan()[0])
    elif( 'backward' in objNew.ti.citem.getRule().lower() or
          'bidirectional' in objNew.ti.citem.getRule().lower() ):
        if( obj2 < objNew ):
            objNew.ti.scope[0] = max(objNew.ti.scope[0],obj2.getSpan()[1])
    return objNew


def applyRule(obj,term):
    """applies obj's rule to term. If the start of term lies within
    the scope of self, then term may be modified by self"""
    if( not obj.ti.citem.getRule() or obj.ti.citem.getRule() == 'terminate'):
        return False
    if(obj.ti.span[0] <= term.ti.span[0] <= obj.ti.scope[1]):
        return True 



def replaceCategory(obj,oldCategory,newCategory):
    objNew = obj.copy()
    for index, item in enumerate(objNew.ti.citem.getCategory()):
        #print index,item,oldCategory
        if item == oldCategory.lower().strip():
            try:
                objNew._tagObject__category[index] = newCategory.lower().strip()
            except:
                del objNew.category[index]
                objNew._tagObject__category.extend([nc.lower().strip() for nc in newCategory])

    return objNew


def setCategory(obj,category):
    objNew = obj.copy()
    objNew._tagObject__category = category
    return objNew



def setSpan(obj,span):
    """set the span within the associated text for this object"""
    objNew = obj.copy()
    objNew._tagObject__spanStart = span[0]
    objNew._tagObject__spanEnd = span[1]
    return objNew



def setPhrase(obj,phrase):
    """set the actual matched phrase used to generate this object"""
    objNew = obj.copy()
    objNew._tagObject__foundPhrase = phrase
    return objNew



def encompasses(obj1,obj2):
    """tests whether obj2 is completely encompassed within obj1
       ??? should we not prune identical span tagObjects???"""
    if( obj1.getSpan()[0] <= obj2.getSpan()[0] and
        obj1.getSpan()[1] >= obj2.getSpan()[1] ):
        return True
    else:
         return False



def getXML(obj):
    return   tagObjectXMLSkel%(obj.getTagID(),xmlScrub(obj.getPhrase()),
                               xmlScrub(obj.getLiteral()),xmlScrub(obj.ti.citem.getCategory()),
                               obj.getSpan()[0],obj.getSpan()[1],
                               obj.getScope()[0],obj.getScope()[1])


class tagObject(object):
    """
    A class that describes terms of interest in the text.
    tagObject is characterized by the following attributes
    1) The contextItem defining the tag
    3) The location of the tag within the text being parsed

    """
    # ci, span, scope,foundPhrase,ConTextCategory,tagid
    def __init__(self, ci, span, scope,foundPhrase,ConTextCategory,tagid):
        """
        item: contextItem used to generate term
        ConTextCategory: category this term is being used for in pyConText

        variants
        """
        newscope = list(scope)
        if( 'forward' in ci.getRule().lower() ):
            newscope[0] = span[1]
        elif( 'backward' in ci.getRule().lower() ):
            newscope[1] = span[0]

        self.ti = titem(ci,span,newscope,foundPhrase,ConTextCategory,tagid)

    def copy(self):
        return tagObject(self.ti.citem,self.ti.span,
                         self.ti.scope,self.ti.foundPhrase,
                         self.ti.ConTextCategory,self.ti.id)


    def getTagID(self):
        return self.ti.id
    def getConTextCategory(self):
        return self.ti.ConTextCategory
    def getFoundPhrase(self):
        """return the actual matched phrase used to generate this object"""
        return self.ti.foundPhrase
    def getScope(self):
        return self.ti.scope
    def getSpan(self):
        """return the span within the associated text for this object"""
        return self.ti.span
    def getConTextItem(self):
        return self.ti.citem
    
    def isA(self,category):
        return self.ti.citem.isA(category)

    def dist(self,obj):
        """returns the minimum distance from the current object and obj.
        Distance is measured as current start to object end or current end to object start"""
        return min(abs(self.__spanEnd-obj.__spanStart),abs(self.__spanStart-obj.__spanEnd))

    def __lt__(self,other): return self.ti.span[0] < other.ti.span[0]
    def __le__(self,other): return self.ti.span[0] <= other.ti.span[0]
    def __eq__(self,other):
        return (self.ti.span[0] == other.ti.span[0] and
                self.ti.span[1] == other.ti.span[1])
    def __ne__(self,other): return self.ti.span[0] != other.ti.span[0] or self.ti.span[1] != other.ti.span[1]
    def __gt__(self,other): return self.ti.span[0] > other.ti.span[0] 
    def __ge__(self,other): return self.ti.span[0] >= other.ti.span[0]


    def __unicode__(self):
        #description = u"""<id> %s </id> """%self.getTagID()
        description =u''
        description+= u"""%s: %s"""%(self.getTagID(),self.getFoundPhrase())
        #description+= u"""<category> %s </category> """%self.getCategory()

        return description
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __repr__(self):
        return unicode(self).encode('utf-8')







