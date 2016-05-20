"""Module containing functions for generating various display options for pyConTextNLP"""
import copy
from ..utils import get_document_markups
from ..utils import get_section_markups

def __sort_by_span(nodes):
    n = copy.copy(nodes)
    n.sort(key=lambda x: x.getSpan())
    return n
def __insert_color(txt,s,c):
    """insert HTML span style into txt. The span will change the color of the
    text located between s[0] and s[1]:
    txt: txt to be modified
    s: span of where to insert tag
    c: color to set the span to"""
    return txt[:s[0]]+'<span style="color: {0};">'.format(c)+\
           txt[s[0]:s[1]]+'</span>'+txt[s[1]:]

def mark_text(txt,nodes,colors = {"name":"red","pet":"blue"},default_color="black"):
    if not nodes:
        return txt
    else:
        n = nodes.pop(-1)
        return mark_text(__insert_color(txt,
                                        n.getSpan(),
                                        colors.get(n.getCategory()[0],default_color)),
                         nodes,
                         colors=colors)

def mark_document_with_html(doc,colors = {"name":"red","pet":"blue"}, default_color="black"):
    """takes a ConTextDocument object and returns an HTML paragraph with marked phrases in the
    object highlighted with the colors coded in colors

    doc: ConTextDocument
    colors: dictionary keyed by ConText category with values valid HTML colors

    """
    return """<p> {0} </p>""".format(" ".join([mark_text(m.graph['__txt'],
                                                 __sort_by_span(m.nodes()),
                                                 colors=colors,
                                                 default_color=default_color) for m in get_document_markups(doc)]))



def mark_document_with_html_sections(doc,colors = {"name":"red","pet":"blue"}, default_color="black"):
    """takes a ConTextDocument object and returns
    a series of sections marked in HTML header tags followed by
    HTML paragraphs with marked phrases in the
    object highlighted with the colors coded in colors

    doc: ConTextDocument
    colors: dictionary keyed by ConText category with values valid HTML colors
    """
    h = """"""

    for hierarchy in doc.getDocumentSections():
        if hierarchy == 'document':
            continue
        for section in hierarchy:
            h += """<h2> {0} </h2>""".format(section)
            # print("## h2: ", section)
        # print("#### Nodes:", context.getSectionNodes(section))
        # print("#### Marked up sentences:", context.getSectionMarkups(section))
    #     h += html.mark_document_with_html(context.getSectionMarkups(section),colors = colors, default_color="black")
    #     print(h)
    #
            h += """<p> {0} </p>""".format(" ".join([mark_text(
                        m.graph['__txt'], __sort_by_span(m.nodes()), colors=colors, default_color=default_color
                    ) for m in get_section_markups(doc,section)
                ]))

    return h
