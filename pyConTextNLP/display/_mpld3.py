"""This module provides pyConTextNLP visualization using matplotlib and mpld3"""

import networkx as nx

def graphDocument(g):
    """ """
    try:
        pos=nx.graphviz_layout(g)
    except:
        pos=nx.spring_layout(g,iterations=20)

    nx.draw_networkx_edges(g,pos,alpha=0.3, edge_color='r')
    xpos = [pos[n][0] for n in g.nodes()]
    ypos = [pos[n][1] for n in g.nodes()]
    text = [n.getPhrase() for n in g.nodes()]
