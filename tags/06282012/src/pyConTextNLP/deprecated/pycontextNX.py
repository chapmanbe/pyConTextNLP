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
import pycontext
import networkx as nx

class pyConTextGraph(object):
    def __init__(self, context):
        self.co = context
        self.graphs = {}
        self.__populate()
        
    def __populate(self):
        self.createRelationGraph()
        self.createAllTagsGraph()
        
    def createRelationGraph(self):
        self.graphs["relations"] = nx.DiGraph()
        root = self.co.getText()
        
        for j in range(self.co.getNumMarkedTargets()):    
            
            term = self.co.getMarkedTarget(j)
            self.graphs["relations"].add_edge(root,term.getBriefDescription())
            modifiers = term.getModifiers()
            for m in modifiers:
                self.graphs["relations"].add_edge(term.getBriefDescription(),m.getBriefDescription())
    def createAllTagsGraph(self):
        self.graphs["alltags"] = nx.DiGraph()
        root = self.co.getText()
        for j in range(self.co.getNumMarkedTargets()):
            term = self.co.getMarkedTarget(j)
            self.graphs["alltags"].add_edge(root,term.getBriefDescription())
        for j in range(self.co.getNumMarkedModifiers()):
            term = self.co.getMarkedModifier(j)
            self.graphs["alltags"].add_edge(root,term.getBriefDescription())
        
    def update(self, graph = None):
        self.createRelationGraph()
        self.createAllTagsGraph()
    def getGraph(self, key):
        return self.graphs.get(key)
    def drawGraph(self, key=None, filename="graph", format="pdf"):
        graph = self.graphs.get(key)
        if( not graph ):
            return
        if( graph.number_of_nodes() > 1 ):
            ag = nx.to_pydot(graph)
            ag.write("%s.%s"%(filename,format),format=format)