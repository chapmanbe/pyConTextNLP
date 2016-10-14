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
"""This is an alternative implementation of the pyConText package where I make
use of graphs to indicate relationships between targets and modifiers. Nodes of
thegraphs are the targets and modifiers identified in the text; edges of the
graphs are relationships between the targets. This provides for much simpler
code than what exists in the other version of pyConText where each object has a
dictionary of __modifies and __modifiedby that must be kept in sync with each
other.

Also it is hoped that the use of a directional graph could ultimately simplify
our itemData structures as we could chain together items"""

import os
version = {}
with open(os.path.join(os.path.dirname(__file__),"version.py")) as f0:
    exec(f0.read(), version)

__version__ = version['__version__']
