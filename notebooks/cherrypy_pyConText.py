import pyConTextNLP.pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData
from textblob import TextBlob
import networkx as nx
import pyConTextNLP.display.html as html
import json
import cherrypy


class pyConTextNLP_REST(object):
    
    mod = itemData.instantiateFromCSVtoitemData(
    "https://raw.githubusercontent.com/chapmanbe/pyConTextNLP/master/KB/lexical_kb_05042016.tsv")
    tar = itemData.instantiateFromCSVtoitemData(
    "https://raw.githubusercontent.com/chapmanbe/pyConTextNLP/master/KB/utah_crit.tsv")

    clrs ={\
    "bowel_obstruction": "blue",
    "inflammation": "blue",
    "definite_negated_existence": "red",
    "probable_negated_existence": "indianred",
    "ambivalent_existence": "orange",
    "probable_existence": "forestgreen",
    "definite_existence": "green",
    "historical": "goldenrod",
    "indication": "pink",
    "acute": "golden"
    } 

    @cherrypy.expose
    def index(self):
        return "Welcome to pyConTextNLP REST API. To start go to /markup_report."

    @cherrypy.expose
    def markup_report(self, report='''IMPRESSION: Evaluation limited by lack of IV contrast; however, no evidence of
                                    bowel obstruction or mass identified within the abdomen or pelvis. 
                                    Non-specific interstitial opacities and bronchiectasis seen at the right
                                    base, suggestive of post-inflammatory changes.
                                    ''',
                                    modifiers=None,
                                    targets=None):
        print("type of modifiers",type(modifiers))
        print("len of modifiers",len(modifiers))
        print(modifiers)
        for m in modifiers:
            print(m)

        if modifiers==None:
            _modifiers = self.mod 
        else:
            _modifiers = itemData.itemData()
            _modifiers.extend(json.loads(modifiers))
        if targets==None:
            _targets=self.tar 
        else:
            _targets = itemData.itemData()
            _targets.extend(json.loads(targets))


        
        context = self.split_sentences(report, _modifiers, _targets) 
        clrs = self.get_colors_dict(_modifiers, _targets)
        return html.mark_document_with_html(context, colors=clrs)


    def markup_sentence(self, s, modifiers, targets, prune_inactive=True):
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

    def split_sentences(self, report, modifiers, targets):
        blob = TextBlob(report.lower())
        count = 0
        rslts = []
        for s in blob.sentences:
            m = self.markup_sentence(s.raw, modifiers, targets)
            rslts.append(m)
        
        context = pyConText.ConTextDocument()
        for r in rslts:
            context.addMarkup(r)

        return context


    def get_colors_dict(self, modifiers, targets):
        # this method will basically assign blue to all targets 
        # and then assigns a different color  for each modifier category         
        #import colorsys
        import randomcolor
        colors = {}
        rcol = randomcolor.RandomColor()
        for t in targets:
            colors[t.getCategory()[0]] = 'blue'
        mm = set([c.getCategory()[0] for c in modifiers]) 
        #HSV = [(x*1.0/len(mm), 0.5, 0.5) for x in range(len(mm))]
        #RGB = map(lambda x: colorsys.hsv_to_rgb(*x), HSV)
        #RGB = lambda: random.randint(0,255) 
        #for m,rgb in zip(mm,RGB):
        for m in mm:
            colors[m] =  rcol.generate()[0]#"rgb{0}".format(rgb)#"rgb({0},{1},{2})".format(RGB(),RGB(),RGB())

        return colors



if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 3030,})
    cherrypy.quickstart(pyConTextNLP_REST())
