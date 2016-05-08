

def get_modifiers(target, markup):
    """
    target: a tagItem node in markup
    markup: a networkx DiGraph representing a ConText markup
    """
    return markup.predecessors(target)
