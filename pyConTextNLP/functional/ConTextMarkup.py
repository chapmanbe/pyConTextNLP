import re
import networkx as nx
import copy
import uuid
from . import tagItem as TI
# from . import templates as tmplts
import itertools
# import multiprocessing as mp

r1 = re.compile(r"""\W""", re.UNICODE)
r2 = re.compile(r"""\s+""", re.UNICODE)
r3 = re.compile(r"""\d""", re.UNICODE)

rlt = re.compile(r"""<""", re.UNICODE)
ramp = re.compile(r"""&""", re.UNICODE)

compiledRegExprs = {}
currentID = 0


def get_tagID():
    return uuid.uuid1().int


def reset_currentID():
    global currentID
    currentID = 0
    return None


def create_ConTextMarkup():
    return nx.DiGraph(__rawText=None,
                      __text=None,
                      __scope=None,
                      __SCOPEUPDATED=None)


def setRawText(markup, txt=u''):
    """
    sets the current txt to txt and resets the current attributes to empty
    values, but does not modify the object archive
    """
    markupNew = markup.copy()
    markupNew.graph["__rawText"] = txt
    markupNew.graph["__text"] = None
    markupNew.graph["__scope"] = None
    markupNew.graph["__SCOPEUPDATED"] = False
    return markupNew


def get_RawText(markup):
    return markup.graph["__rawText"]


def cleanText(markup, stripNonAlphaNumeric=False, stripNumbers=False):
    """Need to rename. applies the regular expression scrubbers to rawTxt"""
    try:
        markupNew = markup.copy()
        if stripNonAlphaNumeric:
            txt = r1.sub(" ", markupNew.graph["__rawText"])
        else:
            txt = markupNew.graph["__rawText"]

        # clean up white spaces
        txt = r2.sub(" ", txt)

        # optionally cleanup numbers
        if stripNumbers:
            txt = r3.sub("", txt)

        markupNew.graph["__text"] = txt
        return markupNew
    except Exception as error:
        print(error)
        print(txt)
        print(type(txt))
        return ""


def get_cleanText(markup):
    return markup.graph["__text"]


def update_scopes(markup):
    """
    update the scopes of all the marked modifiers in the txt. The scope
    of a modifier is limited by its own span, the span of modifiers in the
    same category marked in the text, and modifiers with rule 'terminate'.
    """
    markupNew = nx.DiGraph()
    targets = getConTextModeNodes(markup, "targets")
    modifiers = getConTextModeNodes(markup, "modifier")
    modifier_pairs = itertools.permutations(modifiers, r=2)
    modifiers = [TI.limitScope(m1, m2) for m1, m2 in modifier_pairs]
    markupNew.graph = copy.copy(markup.graph)
    markupNew.graph["__SCOPEUPDATED"] = True
    markupNew.add_nodes_from(modifiers)
    markupNew.add_nodes_from(targets)
    return markupNew


def prune_marks(markup):
    """
    prune Marked objects by deleting any objects that lie within the span of
    another object.
    """
    markupNew = markup.copy()

    marks = markupNew.nodes(data=True)
    if len(marks) < 2:
        return markupNew
    marks.sort()
    nodesToRemove = []
    marks_pairs = itertools.permutations(marks, r=2)
    nodesToRemove = [m2[0] for m1, m2 in marks_pairs if
                         TI.o1_encompasses_o2(m1[0], m2[0])]
    # print("%d nodes to be removed"%len(nodesToRemove))
    markupNew.remove_nodes_from(nodesToRemove)
    markupNew.graph["__pruned"] = True
    return markupNew


def mark_item_in_text(markup, item, ignoreCase=True):
    """
    markup the current text with the current item.
    If ignoreCase is True (default), the regular expression is compiled with
    IGNORECASE."""

    global compiledRegExprs

    if not (item.literal, item.re) in compiledRegExprs:
        if not item.re:
            regExp = r"\b%s\b"%item.getLiteral()
        else:
            regExp = item.re
        if ignoreCase:
            r = re.compile(regExp, re.IGNORECASE | re.UNICODE)
        else:
            r = re.compile(regExp, re.UNICODE)
        # I NEED TI FIX THIS SO THAT I CAN HAVE MULTIPLE
        # REGULAR EXPRESSIONS/LITERAL
        compiledRegExprs[(item.literal, item.re)] = r
    else:
        r = compiledRegExprs[(item.literal, item.re)]
    miter = r.finditer(markup.graph.get("__text", u''))
    terms = []
    for i in miter:
        # ci, span, scope,foundPhrase,ConTextCategory,tagid
        tO = TI.create_tagItem(item,
                               i.span(),
                               i.group(),
                               get_tagID())

        terms.append(tO)
    return terms


def mark_items_in_text(markup, items, mode="target"):
    """tags the sentence for a list of items
    items: a list of contextItems"""
    # ??? Why am I adding mode to both the tag object and
    # the markup node graph???
    markupNew = markup.copy()
    if not items:
        return markup
    for item in items:
        markupNew.add_nodes_from(mark_item_in_text(markupNew, item),
                                 category=mode)
    return markupNew


def keepClosestMarkupRelationships(markup):
    """Initially modifiers may be applied to multiple targets. This function
    computes the text difference between the modifier and each modified
    target and keeps only the minimum distance relationship

    Finally, we make sure that there are no self modifying modifiers
    present (e.g. "free" in the phrase "free air" modifying the
    target "free air").
    """
    markupNew = markup.copy()
    modifiers = markupNew.getConTextModeNodes("modifier")
    for m in modifiers:
        modifiedBy = markupNew.successors(m)
        if modifiedBy and len(modifiedBy) > 1:
            mdist = [(TI.dist(m, mb), mb) for mb in modifiedBy]
            mdist.sort()
            markup.remove_edges_from([(m, mb[1]) for mb in mdist[1:]])
    return markupNew


def getConTextModeNodes(markup, mode):
    nodes = [n[0] for n in markup.nodes(data=True) if n[1]['category'] == mode]
    nodes.sort()
    return nodes


def getMarkedTargets(markup):
    """
    Return the list of marked targets in the current sentence.
    List is sorted by span
    """
    targets = getConTextModeNodes(markup, "target")
    targets.sort()
    return targets


def apply_modifiers(markup):
    """
    Loop through the marked targets and for each target apply the modifiers
    """
    markupNew = markup.copy()
    targets = getConTextModeNodes(markupNew, "target")
    modifiers = getConTextModeNodes(markupNew, "modifier")
    new_edges = [(m, t) for t, m in itertools.product(targets, modifiers) if
                     TI.applyRule(m, t)]
    markupNew.add_edges_from(new_edges)
    return markupNew


def dropMarks(markup, category="exclusion"):
    """Drop any targets that have the category equal to category"""
    markupNew = markup.copy()
    dnodes = [n for n in markupNew.nodes() if TI.isA_tag(n, category)]
    markupNew.remove_nodes_from(dnodes)
    return markupNew


def create_sentence_ConTextMarkup(s, targets, modifiers, ):
    markup = create_ConTextMarkup()
    markup = setRawText(markup, s)
    markup = cleanText(markup)
    markup = mark_items_in_text(markup, modifiers, mode="modifier")
    markup = mark_items_in_text(markup, targets, mode="target")
    markup = prune_marks(markup)
    markup = dropMarks(markup, category='Exclusion')
    # apply modifiers to any targets within the modifiers scope
    markup = apply_modifiers(markup)

    # markup.pruneSelfModifyingRelationships()
    return markup


def mark_sentence(s, items_dict):
    """
    s: string assumed to be sentence
    items_dict: a dictionary of ConTextItems.
        keys are the ConText mode (e.g. "target", "modifier")
        values are the ConTextItems

    This function does the following steps:

    1. Creates a ConTextMarkup item.
    2. Sets the text to the sentence.
    3. Cleans the text.
    4. Marks the text with each item in items_dict
    5. Prune the marks
    6. Drop marks with category 'Exclusion'
    7. Applies the modifiers to the targets

    Function returns the markup which is a NetworkX directed graph.
    """
    markup = create_ConTextMarkup()
    markup = setRawText(markup, s)
    markup = cleanText(markup)

    for mode, items in items_dict.items():
        markup = mark_items_in_text(markup, items, mode=mode)
    markup = prune_marks(markup)
    markup = dropMarks(markup, category='Exclusion')
    markup = apply_modifiers(markup)

    return markup


def mark_sentences_all(sentences, items_dict):
    """
    sentences: a list of strings, each string representing a distinct sentence
    items_dict: a dictionary of ConTextItems

    calls mark_sentence on each sentence in sentence and returns
        results ina list
    """
    return [mark_sentence(s, items_dict) for s in sentences]


def markup2string(mu):
    txt = u'_'*42+"\n"
    txt += 'rawText: {0}\n'.format(get_RawText(mu))
    txt += 'cleanedText: {0}\n'.format(get_cleanText(mu))
    nodes = [n for n in mu.nodes(data=True) if
                 n[1].get('category', '') == 'target']
    nodes.sort()
    for n in nodes:
        txt += "*"*32+"\n"
        txt += "TARGET: {0}\n".format(TI.tagItem2string(n[0]))
        modifiers = mu.predecessors(n[0])
        modifiers.sort()
        for m in modifiers:
            txt += "-"*4+"MODIFIED BY: {0}\n".format(TI.tagItem2string(m))
            mms = mu.predecessors(m)
            if mms:
                for ms in mms:
                    txt += "-"*8+"MODIFIED BY: {0}\n".format(TI.tagItem2string(ms))

    txt += u"_"*42+"\n"
    return txt
