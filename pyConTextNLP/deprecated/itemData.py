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
A module defining the itemData class. itemData objects are the basis tools for text markup.

The module instantiates several instances of this object:
    1) probableNegations
    2) definiteNegations
    3) pseudoNegations
    4) indications
    5) historicals
    6) conjugates
    7) probables
    8) definites
"""
class itemData(list):
	def __init__(self,*args):
		super(itemData,self).__init__(*args)
		self.__numEnteries = 4
		
	def __validate(self,data):
		"""validate that data consists of the correct number of string arguments"""
		try:
			td = type(data)
			if( td != type([]) and td != type(()) and td != type(set([])) ):
				print "data not a valid container type",td
				return False
			if( len(data ) != self.__numEnteries ):
				print "data must have %d elements."%self.__numEnteries
				return False
			for d in data:
				if( type(d) != type('') ):
					print "all data elements must be strings"
					return False
					
			return True
		except Exception, error:
			print "failed in itemData.validate", error
			return False
			
	def append(self,data):
		if(self.__validate(data)):
			super(itemData,self).append(data)
			
	def insert(self,index,data):
		if(self.__validate(data)):
			super(itemData,self).insert(index,data)
	def extend(self,iterable):
		for i in iterable:
			if( not self.__validate(i) ):
				return
		super(itemData,self).extend(iterable)

probableNegations = itemData([
["can rule out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["cannot be excluded","PROBABLE_NEGATED_EXISTENCE",r"""(cannot|can\snot)\sbe\sexcluded""","backward"],
["is not excluded","PROBABLE_NEGATED_EXISTENCE",r"""(is|was|are|were)\snot\sexcluded""",'backward'],
["adequate to rule the patient out against","PROBABLE_NEGATED_EXISTENCE","","forward"],
["can rule him out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not know of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no findings of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["sufficient to rule her out against","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no suggestion of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["adequate to rule him out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["sufficient to rule him out against","PROBABLE_NEGATED_EXISTENCE",r"""sufficient\sto\srule\s(him|her)\sout\sagainst""","forward"],
["not reveal","PROBABLE_NEGATED_EXISTENCE","","forward"],
["can rule the patient out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["adequate to rule her out for","PROBABLE_NEGATED_EXISTENCE",r"""adequate\sto\srule\s(her|him)\sout\sfor""","forward"],
["sufficient to rule her out for","PROBABLE_NEGATED_EXISTENCE",r"""sufficient\sto\srule\s(her|him)\sout\sfor""","forward"],
["adequate to rule out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["can rule the patient out against","PROBABLE_NEGATED_EXISTENCE",r"""can\srule\s(her|him)\sout\sagainst""","forward"],
["can rule him out against","PROBABLE_NEGATED_EXISTENCE",r"""can\srule\s(her|him)\sout\sagainst""","forward"],
["rather than","PROBABLE_NEGATED_EXISTENCE","","forward"],
["nothing","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not exhibit","PROBABLE_NEGATED_EXISTENCE","","forward"],
["checked for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["evaluate for","PROBABLE_NEGATED_EXISTENCE","","forward"], ### SHOULD THIS BE AN INDICATION?
["can rule the patient out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no findings to indicate","PROBABLE_NEGATED_EXISTENCE","","forward"],
["free","PROBABLE_NEGATED_EXISTENCE","","backward"],
["sufficient to rule him out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["can rule out against","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no sign of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no definite","PROBABLE_NEGATED_EXISTENCE", r"""no[\s]*definite""","forward"], #fixes peco #188, #255
["without sign of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["adequate to rule the patient out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["can rule her out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["sufficient to rule him out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no significant","PROBABLE_NEGATED_EXISTENCE","","forward"],
["adequate to rule him out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not feel","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no obvious","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no complaints of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not associated with","PROBABLE_NEGATED_EXISTENCE","","forward"],
["can rule out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["can rule her out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["adequate to rule out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not see","PROBABLE_NEGATED_EXISTENCE","","forward"],
["fails to reveal","PROBABLE_NEGATED_EXISTENCE","","forward"],
["to exclude","PROBABLE_NEGATED_EXISTENCE","","forward"],
["sufficient to rule the patient out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["sufficient to rule out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["unremarkable for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not appreciate","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not complain of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not demonstrate","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not to be","PROBABLE_NEGATED_EXISTENCE","","forward"],
["unlikely","PROBABLE_NEGATED_EXISTENCE","","backward"],
["absence of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["adequate to rule her out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["can rule him out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["denying","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no signs of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no abnormal","PROBABLE_NEGATED_EXISTENCE","","forward"],
["sufficient to rule the patient out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["without indication of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["sufficient to rule her out","PROBABLE_NEGATED_EXISTENCE","","forward"],
["adequate to rule the patient out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["cannot see","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no cause of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["no evidence of","PROBABLE_NEGATED_EXISTENCE","","forward"],
["not known to have","PROBABLE_NEGATED_EXISTENCE","","forward"],
["can rule her out against","PROBABLE_NEGATED_EXISTENCE",r"""can\srule\s(her|him)\sout\sagainst""","forward"],
["sufficient to rule her out for","PROBABLE_NEGATED_EXISTENCE",r"""sufficient\sto\srule\s(her|him)\sout\sfor""","forward"],
["sufficient to rule the patient out against","PROBABLE_NEGATED_EXISTENCE","","forward"],
["sufficient to rule out against","PROBABLE_NEGATED_EXISTENCE","","forward"],
["sufficient to rule out for","PROBABLE_NEGATED_EXISTENCE","","forward"],
["test for","PROBABLE_NEGATED_EXISTENCE","","forward"],
])

definiteNegations = itemData([
["deny","DEFINITE_NEGATED_EXISTENCE","","forward"],
["denied","DEFINITE_NEGATED_EXISTENCE","","forward"],
["denies","DEFINITE_NEGATED_EXISTENCE","","forward"],
["declined","DEFINITE_NEGATED_EXISTENCE","","forward"],
["declines","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled him out against","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule her out against","DEFINITE_NEGATED_EXISTENCE","","forward"],
["are ruled out","DEFINITE_NEGATED_EXISTENCE","","backward"],
["rules the patient out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled her out against","DEFINITE_NEGATED_EXISTENCE","""ruled\s(him|her)\sout\sagainst""","forward"],
["ruled her out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["rules him out for","DEFINITE_NEGATED_EXISTENCE",r"""rules\s(him|her)\sout\sfor""","forward"],
["rules out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["no other", "DEFINITE_NEGATED_EXISTENCE", r"""no[\s]*other""","forward"], #fixes pedoc #265
["ruled the patient out against","DEFINITE_NEGATED_EXISTENCE","","forward"],
["is ruled out","DEFINITE_NEGATED_EXISTENCE","","backward"],
["did rule the patient out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled him out against","DEFINITE_NEGATED_EXISTENCE","","forward"],
["cannot","DEFINITE_NEGATED_EXISTENCE","","forward"],
["negative for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["is negative","DEFINITE_NEGATED_EXISTENCE",r"(is|was) negative","backward"],
["-ve for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["not","DEFINITE_NEGATED_EXISTENCE",r"\bnot\b","forward"],
["never had","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule the patient out against","DEFINITE_NEGATED_EXISTENCE","","forward"],
["patient was not","DEFINITE_NEGATED_EXISTENCE","","forward"],
["has been ruled out","DEFINITE_NEGATED_EXISTENCE","","backward"],
["rules her out for","DEFINITE_NEGATED_EXISTENCE",r"""rules\s(him|her)\sout\sfor""","forward"],
["with no","DEFINITE_NEGATED_EXISTENCE","","forward"],
["not had","DEFINITE_NEGATED_EXISTENCE","","forward"],
["rules him out","DEFINITE_NEGATED_EXISTENCE",r"""rules\s(him|her)\sout""","forward"],
["rules the patient out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule the patient out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule him out against","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled him out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["no new","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled her out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule out against","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule her out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule him out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["free of","DEFINITE_NEGATED_EXISTENCE","","forward"],
["not have","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled the patient out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled out against","DEFINITE_NEGATED_EXISTENCE","","forward"],
["negative examination for","DEFINITE_NEGATED_EXISTENCE",r"negative (examination|study|exam|evaluation) for","forward"],
["rules out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["rules her out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["resolved","DEFINITE_NEGATED_EXISTENCE","","backward"],
["ruled him out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule him out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["no","DEFINITE_NEGATED_EXISTENCE",r"\bno\b","forward"],
["was ruled out","DEFINITE_NEGATED_EXISTENCE","","backward"],
["did rule her out against","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["ruled the patient out for","DEFINITE_NEGATED_EXISTENCE","","forward"],
["never developed","DEFINITE_NEGATED_EXISTENCE","","forward"],
["did rule her out","DEFINITE_NEGATED_EXISTENCE","","forward"],
["without","DEFINITE_NEGATED_EXISTENCE","","forward"],
["have been ruled out","DEFINITE_NEGATED_EXISTENCE","","backward"],
])

pseudoNegations = itemData([
["not only","PSEUDONEG","",""],
["no definite change","PSEUDONEG","","forward"],
["not cause","PSEUDONEG","","forward"], #should have a re for "not (the) cause"
["without difficulty","PSEUDONEG","","forward"],
["not extend","PSEUDONEG","","forward"],
["not necessarily","PSEUDONEG","","forward"],
["not certain whether","PSEUDONEG","","forward"],
["no significant change","PSEUDONEG","","forward"],
["no suspicious change","PSEUDONEG","","forward"],
["no increase","PSEUDONEG","","forward"],
["no significant interval change","PSEUDONEG","","forward"],
["not drain","PSEUDONEG","","forward"],
["gram negative","PSEUDONEG","","forward"],
["no change","PSEUDONEG","","forward"],
#["the examination","PSEUDONEG","","backward"],
#["positive study for","PSEDUONEG",r"positive (study|exam|examination)( for)","forward"],
])

indications = itemData([
["will be ruled out","INDICATION","","backward"],
["can be ruled out","INDICATION","","backward"],
["will be ruled out for","INDICATION","","forward"],
["should be ruled out","INDICATION","","backward"],
#["did not rule out","INDICATION","","backward"],
["rule out","INDICATION",r"(r/o|rule out|\br o\b|r\.o\.|\bro\b)","forward"],
["could be ruled out","INDICATION","","backward"],
#["not ruled out","INDICATION","","backward"],
["ought to be ruled out for","INDICATION","","forward"],
["be ruled out","INDICATION","","backward"],
["could be ruled out for","INDICATION","","forward"],
["must be ruled out","INDICATION","","backward"],
["must be ruled out for","INDICATION","","forward"],
["ought to be ruled out","INDICATION","","backward"],
["can be ruled out for","INDICATION","","forward"],
["rule him out for","INDICATION","","forward"],
["may be ruled out for","INDICATION","","forward"],
["may be ruled out","INDICATION","","backward"],
["is to be ruled out for","INDICATION","","forward"],
["is to be ruled out","INDICATION","","backward"],
["rule him out","INDICATION","","forward"],
["might be ruled out for","INDICATION","","forward"],
["should be ruled out for","INDICATION","","forward"],
["rule her out","INDICATION","","forward"],
["not been ruled out","INDICATION","","backward"],
["might be ruled out","INDICATION","","backward"],
["rule patient out for","INDICATION",r"rule (him|her|patient|the patient|subject) out for","forward"],
["evaluation of","INDICATION",r"evaluation\s(of|for)","forward"],
["evaluation","INDICATION","","bidirectional"],
["being ruled out","INDICATION","","backward"],
["what must be ruled out is","INDICATION","","forward"],
["examination for","INDICATION",r"(study|exam|examination) for","forward"],
["study for detection","INDICATION","","forward"],
["examination","INDICATION",r"\b(examination|exam|study)\b","backward"],
["protocol",'INDICATION','','backward'],
["rule the patient out","INDICATION","","forward"],
["rule out for","INDICATION","","forward"],
["be ruled out for","INDICATION","","forward"],
["rule the patient out for","INDICATION","","forward"]])
"""THIS IS AGE INDETERMINATE
SUBACUTE
RESIDUAL
RESOLUTION OF PRIOR
RESOLUTION OF
resolving
no change in
chaninging
PREVIOUSLY NOTED
UNCHANGED
HAS DIMINISHED
INTERVAL CHANGE IN

"""
historicals = itemData([
["documented","HISTORICAL","","forward"],
["subacute","HISTORICAL","","forward"],
["chronic","HISTORICAL","","forward"],
["previous","HISTORICAL","","forward"], # fixes pedoc #98, 115
["resolving","HISTORICAL","","forward"],
["resolved","HISTORICAL","","backward"],
["previous","HISTORICAL","","forward"],
["interval change","HISTORICAL","","bidirectional"],
["resolution of","HISTORICAL","","forward"],
["clinical history","HISTORICAL","","forward"],
["unchanged","HISTORICAL","","bidirectional"],
["changing","HISTORICAL","","forward"],
["change in","HISTORICAL","","forward"],
["prior","HISTORICAL","","bidirectional"],
["diminished","HISTORICAL","","bidirectional"],
["sequelae of","HISTORICAL","","forward"],
["prior study", "HISTORICAL","","bidirectional"],
])

conjugates = itemData([
#["with","CONJ","","terminate"], # fixes pedoc 131 scope
["involving","CONJ","","terminate"], # proposed fix for pedoc #153
["as a secondary cause for","CONJ","","terminate"],
["as the secondary etiology for","CONJ","","terminate"],
["as a secondary source of","CONJ","","terminate"],
["as an etiology of","CONJ","","terminate"],
["as the secondary reason of","CONJ","","terminate"],
["as the secondary origin of","CONJ","","terminate"],
["as an secondary reason for","CONJ","","terminate"],
["as an secondary reason of","CONJ","","terminate"],
["reason for","CONJ","","terminate"],
["still","CONJ","","terminate"],
["source of","CONJ","","terminate"],
["except","CONJ","","terminate"],
["etiology of","CONJ","","terminate"],
["as a cause of","CONJ","","terminate"],
["as a source of","CONJ","","terminate"],
["as the secondary etiology of","CONJ","","terminate"],
["as an reason for","CONJ","","terminate"],
["as a etiology for","CONJ","","terminate"],
["as a secondary origin for","CONJ","","terminate"],
["etiology for","CONJ","","terminate"],
["reasons for","CONJ","","terminate"],
["as a secondary cause of","CONJ","","terminate"],
["aside from","CONJ","","terminate"],
["as the origin of","CONJ","","terminate"],
["though","CONJ","","terminate"],
["which","CONJ","","terminate"],
["cause of","CONJ","","terminate"],
["as the secondary cause for","CONJ","","terminate"],
["as a source for","CONJ","","terminate"],
["as an origin for","CONJ","","terminate"],
["as a secondary origin of","CONJ","","terminate"],
["as the etiology for","CONJ","","terminate"],
["other possibilities of","CONJ","","terminate"],
["as an etiology for","CONJ","","terminate"],
["origins for","CONJ","","terminate"],
["as the secondary reason for","CONJ","","terminate"],
["as the secondary origin for","CONJ","","terminate"],
["as an reason of","CONJ","","terminate"],
["origin for","CONJ","","terminate"],
["as a cause for","CONJ","","terminate"],
["however","CONJ","","terminate"],
["secondary to","CONJ","","terminate"],
["although","CONJ","","terminate"],
["as an secondary source of","CONJ","","terminate"],
["as an source of","CONJ","","terminate"],
["as an cause for","CONJ","","terminate"],
["as the secondary cause of","CONJ","","terminate"],
["as a secondary reason of","CONJ","","terminate"],
["as the etiology of","CONJ","","terminate"],
["as an source for","CONJ","","terminate"],
["as an secondary etiology of","CONJ","","terminate"],
["reasons of","CONJ","","terminate"],
["as an cause of","CONJ","","terminate"],
["as an secondary cause for","CONJ","","terminate"],
["as a reason of","CONJ","","terminate"],
["but","CONJ","","terminate"],
["as the secondary source of","CONJ","","terminate"],
["as a etiology of","CONJ","","terminate"],
["reason of","CONJ","","terminate"],
["causes for","CONJ","","terminate"],
["yet","CONJ","","terminate"],
["as a secondary etiology for","CONJ","","terminate"],
["as the origin for","CONJ","","terminate"],
["as the reason for","CONJ","","terminate"],
["trigger event for","CONJ","","terminate"],
["as the reason of","CONJ","","terminate"],
["cause for","CONJ","","terminate"],
["as a reason for","CONJ","","terminate"],
["as an secondary cause of","CONJ","","terminate"],
["sources of","CONJ","","terminate"],
["as the cause for","CONJ","","terminate"],
["as the source of","CONJ","","terminate"],
["as the source for","CONJ","","terminate"],
["origin of","CONJ","","terminate"],
["causes of","CONJ","","terminate"],
["sources for","CONJ","","terminate"],
["as a secondary source for","CONJ","","terminate"],
["apart from","CONJ","","terminate"],
["source for","CONJ","","terminate"],
["as an secondary origin for","CONJ","","terminate"],
["origins of","CONJ","","terminate"],
["as an origin of","CONJ","","terminate"],
["as an secondary source for","CONJ","","terminate"],
["nevertheless","CONJ","","terminate"],
["as the secondary source for","CONJ","","terminate"],
["as a secondary reason for","CONJ","","terminate"],
["as an secondary etiology for","CONJ","","terminate"],
["as the cause of","CONJ","","terminate"],
["as a secondary etiology of","CONJ","","terminate"],
["as an secondary origin of","CONJ","","terminate"]])

probables = itemData([
["seen best","PROBABLE_EXISTENCE","",""], # fixes pedoc #126 uncertainty
["consistent with","PROBABLE_EXISTENCE","","forward"],
["evidence","PROBABLE_EXISTENCE","","forward"],
["suggestive","PROBABLE_EXISTENCE","","forward"],
#["not excluded", "POST-UNCERTAINTY",r"""not\sexcluded""","backward"], #fixes pedoc #139
["appear","PROBABLE_EXISTENCE","\bappear\b","bidirectional"], # fixes pedoc #270 uncertainty
#["definite","DEFINITE EXISTENCE","","forward"],
["may represent","PROBABLE_EXISTENCE",r"""(may|might)\srepresent""","forward"],
["appears to be","PROBABLE_EXISTENCE","","forward"],
["compatible with","PROBABLE_EXISTENCE","","forward"],
["convincing","PROBABLE_EXISTENCE","","forward"],
["suggest","PROBABLE_EXISTENCE",r"\bsuggest\b","forward"],
["represents","PROBABLE_EXISTENCE","","forward"],
["certain if","UNCERTAINTY","","forward"],
["suspicious","PROBABLE_EXISTENCE","","forward"],
["seen","PROBABLE_EXISTENCE",r"(seen|visualized|observed)","backward"],
["noted","PROBABLE_EXISTENCE","","backward"],
["worrisome","PROBABLE_EXISTENCE","","forward"],
["identified","PROBABLE_EXISTENCE","","backward"],
["suspicous","PROBABLE_EXISTENCE","","forward"],
["likely","PROBABLE_EXISTENCE","","bidirectional"],
["versus","PROBABLE_EXISTENCE","","bidirectional"],
["equivocal","PROBABLE_EXISTENCE","",'bidirectional']
])

definites = itemData([
["positive examination for","DEFINITE_EXISTENCE","","forward"], # fixes pedoc #126 uncertainty
["obvious","DEFINITE_EXISTENCE","","forward"],
["definite","DEFINITE_EXISTENCE","","forward"],
["positive study for","PSEDUONEG",r"positive (study|exam|examination)( for)","forward"],
])