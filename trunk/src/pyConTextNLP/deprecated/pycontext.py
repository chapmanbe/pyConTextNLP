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
3) pycontext: a class that implements the context algorithm 

"""
import re
import copy

        
class termObject(object):
    """
    A class that describes terms of interest in the text.
    termObject is characterized by the following attributes
    1) The textual term being sought
    2) The categorty this term fits in (e.g. finding)
    3) The location of the term within the text being parsed
    4) What other terms modify this term
    5) What terms this term modifies 
    """
    def __init__(self,term, category,regExp,*args):
        """
        term: textual term to define object
        category: category for this term
        regExp: a regular expressiont that is used to catch term and its
        variants
        """
        self.__term = term
        self.__category = category.lower()
        self.__start = 0 # where the term occurs in the sentence
        self.__spanStart = 99
        self.__spanEnd = 77
        self.__regExp = regExp
        self.__foundPhrase = ''
        self.__modifiedBy = {} # another object that modifies this object
        self.__modifies = {} # another object modified by this object
    
    def getBriefDescription(self):
        return """%s (%s) <<%s>>"""%(self.getTerm(),self.getPhrase(),self.getCategory())
    def getTerm(self):
        """returns the term defining this object"""
        return self.__term
    def getCategory(self):
        """returns the category (e.g. CONJUNCTION) for this object"""
        return self.__category
    def setStart(self,start):
        """set the start location for this object in the associated text.
        Is this redudant with span???"""
        self.__start = start
    def getStart(self):
        """return the start location for this object"""
        return self.__start
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
    def getModifiedBy(self):
        """returns the object modifying this object.
        Why do I only have one object as a modifier???"""
        return self.__modifiedBy
    def setModifiedBy(self,obj):
        """sets the object modifying this object"""
        self.__modifiedBy = obj
    def dropModifies(self,obj):
        """remove obj from the list of objects modified by the current object"""
        try:
            self.__modifies[obj.getCategory()].remove(obj)
        except:
            pass
    def addModifies(self,obj):
        """add obj to the list of objects modified by the current object. There
        is currently no safety check that obj is valid"""
        tmp = self.__modifies.get(obj.getCategory(),[])
        tmp.append(obj)
        self.__modifies[obj.getCategory()] = tmp
        
    def dist(self,obj):
        """returns the minimum distance from the current object and obj.
        Distance is measured as current start to object end or current end to object start"""
        return min(abs(self.__spanEnd-obj.__spanStart),abs(self.__spanStart-obj.__spanEnd))

    def updateModifiedBy(self,obj):
        """Adds obj to the collection of objects modified by self"""
        modifier = self.__modifiedBy.get(obj.getCategory())
        
        if( not modifier ):
            self.__modifiedBy[obj.getCategory()] = obj
            obj.addModifies(self)
        else:
            if( self.dist(obj) < self.dist(modifier) ):
                modifier.dropModifies(self)
                self.__modifiedBy[obj.getCategory()]  = obj
                obj.addModifies(self)

                    
    def __lt__(self,other): return self.__start < other.__start
    def __le__(self,other): return self.__start <= other.__start
    def __eq__(self,other): 
        return (self.__start == other.__start and 
                self.__spanStart == other.__spanStart and 
                self.__spanEnd == other.__spanEnd)
    def __ne__(self,other): return self.__start != other.__start
    def __gt__(self,other): return self.__start > other.__start
    def __ge__(self,other): return self.__start >= other.__start
    def encompasses(self,other):
        """tests whether other is completely encompassed with the current object"""
        if( self.__spanStart <= other.__spanStart and 
            self.__spanEnd >= other.__spanEnd ):
            return True
        else:
             return False
    def __str__(self):
        txt = """term<<%s>>; category<<%s>>; span<<%d, %d>>; matched phrase<<%s>>"""%\
                (self.__term,self.__category,self.__spanStart,self.__spanEnd,self.__foundPhrase)
        if( self.__modifiedBy): txt += "; Modified by<<%s>>"%self.renderModifiedBy()
        return txt
    def renderModifiedBy(self):
        txt = ''
        keys = self.__modifiedBy.keys()
        for k in keys:
            obj = self.__modifiedBy[k]
            txt += " %s[%s]@%d"%(obj.getPhrase(),obj.getCategory(),obj.getStart())
        return txt
    def getNumModifiers(self):
        """return the number of ojbects modifying the current object"""
        return len(self.__modifiedBy)
    def getModifier(self,i=0):
        """This function strikes me as being very problematic since keys are not
        ordered"""
        try:
            keys = self.__modifiedBy.keys()
            return self.__modifiedBy[keys[i]]
        except:
            return None
    def isModifiedByOr(self,terms):
        """"returns true if self is modified by any term in the list terms"""
        if( not self.__modifiedBy ):
            return False

        for t in terms:
            if( self.isModifiedBy(t) ):
                return True
        return False


    def isModifiedByAnd(self,terms):
        """return True if self is modified by all items in the list terms"""
        if( not self.__modifiedBy ):
            return False
        if( type(terms) == type('') ):
            return self.isModifiedBy(terms)
        for t in terms:
            if( not self.isModifiedBy(t) ):
                return False
        return True

    def isModifiedBy(self,term, returnModifier=False):
        """tests whether self is modified by term. Optionally return the actual modifier"""
        if( not self.__modifiedBy ):
            return False
        if( type(term) != type('') ):
            raise TypeError("term must be a string")
        keys = self.__modifiedBy.keys()
        for k in keys:
            modifier = self.__modifiedBy[k]
            if( term.lower() in modifier.getCategory().lower() ):
                if( returnModifier):
                    return modifier
                else:
                    return True 
        return False

    def getModifiers(self):
        """
        returns the dictionary of objects modifying the current object.
        I should probably return a copy
        """
        
        return self.__modifiedBy.values()
class tagObject(termObject):
    """
    A class that describes and manages tag of interest in the text
    Adds the concept of a rule to termObject as well as the concept of a scope
    """
    def __init__(self,term,category,regexp,*args):
        """
        term, category and regexp are the same as for termObject
        *args contains the rule and scope for the object
        """
        super(tagObject,self).__init__(term,category,regexp,args)
                                      
        self.__rule = args[0].lower()
        self.__scope = list(args[1][:])
        self.__SCOPEUPDATED = False 
    def setScope(self):
        """
        applies the objects own rule and span to modify the object's scope
        Currently only "forward" and "backward" rules are implemented
        """
        
        if( 'forward' in self.__rule.lower() ):
            self.__scope[0] = self.getSpan()[1]
        elif( 'backward' in self.__rule.lower() ):
            self.__scope[1] = self.getSpan()[0]
            
    def __str__(self):
        txt = super(tagObject,self).__str__()
        txt += """; rule<<%s>>; scope<<%d,%d>>"""%(self.__rule,self.__scope[0],self.__scope[1])
        return txt
    def getScope(self):
        return self.__scope
    def getRule(self):
        return self.__rule
 
    def limitScope(self,obj):
        """If self and obj are of the same category or if obj has a rule of
        'terminate', use the span of obj to
        update the scope of self"""
        if( not self.getRule() or self.getRule()== 'terminate' or 
             (self.getCategory() != obj.getCategory() and obj.getRule() != 'terminate')):
            return
        if( 'forward' in self.__rule.lower() ):
            if( obj > self ):
                self.__scope[1] = min(self.__scope[1],obj.getSpan()[0])
        elif( 'backward' in self.__rule.lower() ):
            if( obj < self ):
                self.__scope[0] = max(self.__scope[0],obj.getSpan()[1])

    def applyRule(self,term):
        """applies self's rule to term. If the start of term lines within
        the span of self, then term may be modified by self"""
        if( not self.getRule() or self.getRule() == 'terminate'):
            return
        if(self.__scope[0] <= term.getStart() <= self.__scope[1]):
            term.updateModifiedBy(self)

        
class pycontext(object):
    """
    base class for context.
    build around markedTargets a list of termObjects representing desired terms
    found in text and markedModifiers, tagObjects found in the text
    """
    # regular expressions for cleaning text
    r1 = re.compile(r"""\W""")
    r2 = re.compile(r"""\s+""")
    r3 = re.compile(r"""\d""")
    # regular expression for identifying word boundaries (used for more
    # complex rule specifications
    rb = re.compile(r"""\b""")
    def __init__(self,txt=''):
        """txt is the string to parse"""
        # __archive is for multisentence text processing. A markup is done
        # for each sentence and then put in the archives when the next sentence
        # is processed
        self.__archive = {}
        self.__currentSentence = 0
        self.__rawTxt = txt
        self.__txt = None
        self.__markedTargets = []
        self.__markedModifiers = []
        self.__scope = None
        self.__SCOPEUPDATED = False

        # regular expressions for finding text
        self.res = {}


    def reset(self):
        """deletes all archived values and sets all class attributes to empty or
        zero values
        """
        self.__archive = {}
        self.__markedTargets = []
        self.__markedModifiers = []
        self.__scope = None
        self.__SCOPEUPDATED 
        self.__currentSentence = 0
    def commit(self):
        """
        takes the values stored in current attributes and copies them to the
        object archive
        """
        # I'm not sure if I want to be using copy here
        self.__archive[self.__currentSentence] = (copy.copy(self.__rawTxt),
                                                  copy.copy(self.__txt),
                                                  copy.copy(self.__markedTargets),
                                                  copy.copy(self.__markedModifiers),
                                                  copy.copy(self.__scope),
                                                  copy.copy(self.__SCOPEUPDATED))
        self.__currentSentence += 1
        self.setTxt()
    def setSentence(self,num):
        """
        set the current context to sentence num in the archive
        """
        self.__rawTxt = copy.copy(self.__archive[num][0])
        self.__txt = copy.copy(self.__archive[num][1])
        self.__markedTargets = copy.copy(self.__archive[num][2])
        self.__markedModifiers = copy.copy(self.__archive[num][3])
        self.__scope = copy.copy(self.__archive[num][4])
        self.__SCOPEUPDATED = copy.copy(self.__archive[num])

                                        
    def setTxt(self,txt=''):
        """
        sets the current txt to txt and resets the current attributes to empty
        values, but does not modify the object archive
        """
        self.__rawTxt = txt
        self.__txt = None
        self.__markedTargets = []
        self.__markedModifiers = []
        self.__scope = None
        self.__SCOPEUPDATED = False
        
    def getText(self):
        return self.__txt
    def getNumberSentences(self):
        return len(self.__archive)
    def getCurrentSentenceNumber(self):
        return self.__currentSentence
    def incrementSentence(self):
        pass
    def getNumMarkedTargets(self):
        return len(self.__markedTargets)
    def getNumMarkedModifiers(self):
        return len(self.__markedModifiers)
    def getMarkedTarget(self,i=0):
        try:
            return self.__markedTargets[i]
        except:
            return None
    def getMarkedModifier(self,i=0):
        try:
            return self.__markedModifiers[i]
        except:
            return None
    def getCleanTxt(self,stripNumbers=False):
        """Need to rename. applies the regular expression scrubbers to rawTxt"""
        self.__txt = self.r1.sub(" ",self.__rawTxt)
        self.__txt = self.r2.sub(" ",self.__txt)
        if( stripNumbers ):
            self.__txt = self.r3.sub("",self.__txt)
            
        self.__scope= (0,len(self.__txt))
    def __str__(self):
        txt = ''
        txt += self.renderMarkedTargets()
        #txt += """TAGS""".center(60)+"\n\n"
        for term in self.__markedModifiers:
            txt += term.__str__()+"\n"
        txt += "-"*60
        return txt
    def renderMarkedTargets(self):
        if( not self.__markedTargets ):
            return ''
        txt = """TERMS""".center(60)+"\n\n"
        for term in self.__markedTargets:
            txt += term.__str__()+"\n"
        return txt
    def renderMarkedModifiers(self):
        if( not self.__markedModifiers ):
            return ''
        txt = """TAGS""".center(60)+"\n\n"
        for term in self.__markedModifiers:
            txt += term.__str__()+"\n"
        return txt

    def updateScopes(self):
        """
        update the scopes of all the marked modifiers in the txt. The scope
        of a modifier is limited by its own span and the and the span of
        modifiers in the same category marked in the text.
        """
        self.__SCOPEUPDATED = True
        # make sure each tag has its own self-limited scope
        for modifier in self.__markedModifiers:
            modifier.setScope()

        # Now limit scope based on the domains of the spans of the other
        # modifier
        for i in range(len(self.__markedModifiers)-1):
            modifier = self.__markedModifiers[i]
            for j in range(i+1,len(self.__markedModifiers)):
                modifier2 = self.__markedModifiers[j]
                modifier.limitScope(modifier2)
                modifier2.limitScope(modifier)

    def markTargets(self,terms,objType = termObject):
        """tags the sentence for a list of terms
        terms: a list of terms each term is a tuple with the following two elements: 
        term[0]--the term to tag
        term[1]--the category for the tag (e.g. "EXCLUDE")
        term[2]--a regular expression to express a general form of term. Pass an empty string if not desired"""
        self.__markedTargets = []
        for term in terms:
            self.__markedTargets.extend(self.markText(term,mode=objType))

    def markModifiers(self,terms,objType=tagObject):
        """tags the sentence for a list of terms
        terms: a list of terms each term is a tuple with the following two elements: 
        term[0]--the term to tag
        term[1]--the category for the tag (e.g. "EXCLUDE")
        term[2]--a regular expression to express a general form of term. Pass an empty string if not desired
        term[3]--a rule for the tag"""
        self.__markedModifiers = []
        for term in terms:
            self.__markedModifiers.extend(self.markText(term,mode=tagObject))
        self.__SCOPEUPDATED = False
                                


         
    def markText(self,term, mode=termObject, ignoreCase=True ):
        """
        markup the current text with the current term.
        If ignoreCase is True (default), the regular expression is compiled with
        IGNORECASE.
        
        Note that the regular expression is only generated once. So the case sensitivity
        will be determined for all subsequent uses by the first application of the term
        term is a tuple with the following elements
        term[0]--the text to tag
        term[1]--the category
        term[2]--a regular expression or empty string
        term[3]--a rule (if mode='Modifier')"""
            
        if( not self.__txt ):
            self.getCleanTxt()

        # See if we have already created a regular expression

        if(not self.res.has_key(term[0]) ):
            if(not term[2]):
                regExp = term[0]
            else:
                regExp = term[2]
            r = re.compile(regExp, re.IGNORECASE)
            self.res[term[0]] = r
        else:
            r = self.res[term[0]]
        iter = r.finditer(self.__txt)
        terms=[]
        for i in iter:
            tO = mode(term[0], term[1],term[2],term[3],self.__scope)
    
            tO.setStart(i.start())
            tO.setSpan(i.span())
            tO.setPhrase(i.group())
            terms.append(tO)
        return terms

    def pruneMarks(self):    
        """
        prune Marked objects by deleting any objects that lie within the span of
        another object. Currently modifiers and targets are treated separately
        """
        # how to deal with the modifies and modifiedBy lists?
        self.__prune_marks(self.__markedModifiers)
        self.__prune_marks(self.__markedTargets)
    def __prune_marks(self, marks):
        marks.sort()
        for t1 in marks:
            for t2 in marks:
                if( not t1 is t2 ):
                    if( t1.encompasses(t2) ):
                        # Need to add an adjustment of the
                        # targets modified by t2
                        marks.remove(t2)
                    elif( t2.encompasses(t1) ):
                        marks.remove(t1)
                        break        
    def dropMarks(self,category="exclusion"):
        """Drop any targets that have the category equal to category"""
        # how to deal with the modifies and modifiedBy lists?
        for obj in self.__markedTargets:
            if( category.lower() in obj.getCategory() ):
                self.__markedTargets.remove(obj)
        for obj in self.__markedModifiers:
            if( obj.getCategory() == category ):
                self.__markedModifiers.remove(obj)                

    def applyModifiers(self):
        """
        If the scope has not yet been updated, do this first.
        
        Loop through the marked targets and for each target apply the modifiers
        """
        # make sure markedModifiers is sorted
        if( not self.__SCOPEUPDATED ):
            self.updateScopes()
        for term in self.__markedTargets:
            for modifier in self.__markedModifiers:
                modifier.applyRule(term)
    def getMarkedTargets(self):
        """
        Return the list of marked targets in the current sentence
        """
        return self.__markedTargets # should I be returning a copy instead?
    def getNumMarkedTargets(self):
        """
        Return the number of marked targets in the current sentence
        """
        return len(self.__markedTargets)
    def getMarkedTarget(self,i=0):
        """
        return the ith marked target
        """

        return self.__markedTargets[i]
           


        
