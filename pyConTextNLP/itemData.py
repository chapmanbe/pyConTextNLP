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
A module defining the contextItem class.
"""
import yaml
import urllib.request, urllib.error, urllib.parse


def _get_fileobj(_file):
    if not urllib.parse.urlparse(_file).scheme:
        _file = "file://"+_file
    return urllib.request.urlopen(_file, data=None)

def get_items(_file):
    f0 = _get_fileobj(_file)
    context_items =  [contextItem((d["Lex"],
                                   d["Type"],
                                   r"%s"%d["Regex"],
                                   d["Direction"])) for d in yaml.load_all(f0)]
    f0.close()
    return context_items


class contextItem(object):


    def __init__(self, args):
        self.__literal = args[0]
        cs = args[1].split(",")
        self.__category = []
        for c in cs:
            self.__category.append(c.lower().strip())
        self.__re = r"%s"%args[2] # I need to figure out how to read this raw string in properly
        self.__rule = args[3].lower()

        # generate regex from literal if no regex provided
        if not self.__re:
            self.__re = r"\b{}\b".format(self.__literal)

    def getLiteral(self):
        """return the literal associated with this item"""
        return self.__literal
    def getCategory(self):
        """return the list of categories associated with this item"""
        return self.__category[:]
    def categoryString(self):
        """return the categories as a string delimited by '_'"""
        return '_'.join(self.__category)


    def isA(self,testCategory):
        """test whether testCategory is one of the categories associated with self"""
        try:
            return testCategory.lower().strip() in self.__category
        except:
            for tc in testCategory:
                if( tc.lower().strip() in self.__category ):
                    return True
            return False

    def getRE(self):
        return self.__re
    def getRule(self):
        return self.__rule
    def __str__(self):
        txt = """literal<<{0}>>; category<<{1}>>; re<<{2}>>; rule<<{3}>>""".format(
            self.__literal,self.__category,self.__re, self.__rule)
        return txt
    def __repr__(self):
        return self.__str__()

