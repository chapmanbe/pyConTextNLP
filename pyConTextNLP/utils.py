""" """

def get_document_markups(document):
    """ Given a ConTextDocument return an ordered list of the ConTextmarkup objects consistituting the document"""
    tmp = [(e[1],e[2]['sentenceNumber']) for e in document.getDocument().edges(data=True) if
           e[2].get('category') == 'markup']
    tmp.sort(key=lambda x:x[1])
    return [t[0] for t in tmp]

def get_section_markups(document, sectionLabel):
    """ Given a ConTextDocument and sectionLabel, return an ordered list of the ConTextmarkup objects in that section"""
    tmp = [(e[1],e[2]['sentenceNumber']) for e in document.getDocument().out_edges(sectionLabel, data=True) if
           e[2].get('category') == 'markup']
    tmp.sort(key=lambda x:x[1])
    return [t[0] for t in tmp]

def conceptInDocument(document, concept):
    """tests whether concept is in any nodes of document"""
    pass
