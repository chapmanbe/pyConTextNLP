from pyConTextNLP import pyConTextGraph as pyConText
import networkx as nx

def test_ConTextMarkup():
    assert isinstance(pyConText.ConTextMarkup(), nx.DiGraph)


def markup_sentence(s, modifiers, targets, prune_inactive=True):
    """
    """
    markup = pyConText.ConTextMarkup()
    markup.setRawText(s)
    markup.cleanText()
    markup.markItems(modifiers, mode="modifier")
    markup.markItems(targets, mode="target")
    markup.pruneMarks()
    markup.dropMarks('Exclusion')
    # apply modifiers to any targets within the modifiers scope
    markup.applyModifiers()
    markup.pruneSelfModifyingRelationships()
    if prune_inactive:
        markup.dropInactiveModifiers()
    return markup
