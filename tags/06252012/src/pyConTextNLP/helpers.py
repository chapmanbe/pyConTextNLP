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

def sentenceSplitter(txt):
    txt = txt.split()
    sentences = []
    wordLoc = 0
    digits = set('0123456789')
    
    while(wordLoc < len(txt) ):
        currentWord = txt[wordLoc]
        if( currentWord[-1] in '.?!' ):
            if( currentWord in  ['.','Dr.','Mr.','Mrs','Ms.','M.D.','Ph.D.','D.M.D.','R.N.','B.A.','A.B.','B.S.','q.','viz.','e.g.']):
                wordLoc += 1
            elif( set('0123456789').intersection(currentWord) and not set('()').intersection(currentWord)):
                wordLoc += 1
            else:
                sentences.append(' '.join(txt[:wordLoc+1])) 
                txt = txt[wordLoc+1:]
                wordLoc = 0
        else:
            wordLoc += 1
    return sentences