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
The module defines a class sentenceSplitter that defines how sentence splitting is to be done including
exception terms that include sentence termination terms but do not indicate a termination (e.g. Mrs.).
The exception terms are contained in the attribute exceptionTerms. Terms can be added or deleted
through the class methods addExceptionTerms and deleteExceptionTerms. A short list of default terms
common in English texts are included in the attribute defaultExceptions. By default these are
used when a sentenceSplitter instance is created.
"""
class sentenceSplitter(object):
    """Class for splitting sentences"""

    def __init__(self, useDefaults=True, useCaseVariants=True):
        """
        useDefaults: Populate the exceptionTerms with default values
        useCaseVariants: add upper and lower case variants of terms also
        """

        self.defaultExceptions = ['.','Dr.','Mr.','Mrs.','Ms.','M.D.',
                               'Ph.D.','D.M.D.','R.N.','B.A.','A.B.',
                               'B.S.','M.S.','q.','viz.','e.g.']
        self.exceptionTerms = set(())

        self.digits = set('0123456789')
        if useDefaults:
            for term in self.defaultExceptions:
                try:
                    self.exceptionTerms.add(term)
                    if useCaseVariants:
                        self.exceptionTerms.add(term.lower())
                        self.exceptionTerms.add(term.upper())
                except TypeError:
                    print("Terms must be of type string. You provided {0} which is a {1}".format(term,type(term)))

    def addExceptionTerms(self, *terms, **kwargs): #addCaseVariants=True):
        """add exception terms to list of terms not to terminate sentence at.
        If keyword argument addCaseVariants = True is provided, then also add the lower and upper case variants to the list """
        addCaseVariants = kwargs.pop('addCaseVariants', False)
        for t in terms:
            self.exceptionTerms.add(t)
            if addCaseVariants:
                self.exceptionTerms.add(t.lower())
                self.exceptionTerms.add(t.upper())

    def getExceptionTerms(self):
        return self.exceptionTerms
    def deleteExceptionTerms(self,*terms, **kwargs): #deleteCaseVariants=True):
        """delete exception terms from list of terms not to terminate sentence at.
        If keyword argument deleteCaseVariants = True is provided, then also delete the lower and upper case variants from the list"""
        deleteCaseVariants = kwargs.pop('deleteCaseVariants', False)
        for t in terms:
            self.exceptionTerms.discard(t)
            if deleteCaseVariants:
                self.exceptionTerms.discard(t.lower())
                self.exceptionTerms.discard(t.upper())

    def splitSentences(self,txt):
        """
        Splt txt into sentences a list of sentences is returned
        """
        txt = txt.split()
        sentences = []
        wordLoc = 0

        while wordLoc < len(txt):
            currentWord = txt[wordLoc]
            if currentWord[-1] in '.?!':
                if currentWord in  self.exceptionTerms:
                    wordLoc += 1
                # per discussion with A.G. dropped this exception, since assuming numbers only use decimal points if there
                # are actual decimal point digits expressed and thus the period would not be the last character of the word.
                #elif( self.digits.intersection(currentWord) and
                        #not set('()').intersection(currentWord)): # word doesn't include parentheses. Is this necessary?
                    #wordLoc += 1
                else:
                    sentences.append(' '.join(txt[:wordLoc+1]))
                    txt = txt[wordLoc+1:]
                    wordLoc = 0
            else:
                wordLoc += 1

        # if any texts remains (due to failure to identify a final sentence termination,
        # then take all remaining text and put into a sentence
        if txt:
            sentences.append(' '.join(txt) )

        return sentences
