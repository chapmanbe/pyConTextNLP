import unittest
import pyConTextNLP.functional.ConTextItem as CI
import pyConTextNLP.functional.tagItem as TI
import pyConTextNLP.functional.ConTextMarkup as CM
import pyConTextNLP.functional.ConTextDocument as CD
from textblob import TextBlob
import networkx as nx

class functional_test_ConTextItem(unittest.TestCase):
    def setUp(self):
        # create a sample image in memory

        self.items = {"targets":[ ["pulmonary embolism",
                        "PULMONARY_EMBOLISM",
                        r"""pulmonary\s(artery )?(embol[a-z]+)""",""]],
                       "modifiers":[["no gross evidence of",
                        "PROBABLE_NEGATED_EXISTENCE,HEDGE_TERM","","forward"]]}
        self.files = {}
        #options['infile'] = os.path.join(UTAHDATA,"CTPA PHI - main data set, 2015-04-19.xls")
        self.files['lexical_kb'] = ["https://raw.githubusercontent.com/chapmanbe/pyConTextNLP/master/KB/lexical_kb_04292013.tsv",
                                "https://raw.githubusercontent.com/chapmanbe/pyConTextNLP/master/KB/criticalfinder_generalized_modifiers.tsv",
                                "https://raw.githubusercontent.com/chapmanbe/pyConTextNLP/master/KB/critical_modifiers.tsv"]
        self.files['domain_kb'] = ["https://raw.githubusercontent.com/chapmanbe/pyConTextNLP/master/KB/utah_crit.tsv"]#[os.path.join(DATADIR2,"pe_kb.tsv")]


    def tearDown(self):
        self.items = 0
    def test_create_ConTextItem(self):
        ci = CI.create_ConTextItem(self.items['targets'][0])
        assert ci.re == self.items['targets'][0][2]
        assert ci.category == (self.items['targets'][0][1].lower().strip(),)

    def test_create_ConTextItem2(self):
        ci = CI.create_ConTextItem(self.items['modifiers'][0])
        assert ci.re == self.items['modifiers'][0][0].lower().strip()
        assert len(ci.category) == 2

    def test_isA(self):
        ci = CI.create_ConTextItem(self.items["modifiers"][0])
        assert CI.isA(ci,"HEART_DISEASE") == False
        assert CI.isA(ci,"HEDGE_TERM") == True
    def test_test_rule(self):
        ci = CI.create_ConTextItem(self.items["modifiers"][0])
        assert CI.test_rule(ci,"Forward") == True
        assert CI.test_rule(ci,"forward") == True
        assert CI.test_rule(ci,"bidirection") == False

    def test_read_ConTextItem0(self):
        items, headers = CI.readConTextItems(self.files['lexical_kb'][0])
        assert items

    def test_read_ConTextItem1(self):
        items, headers = CI.readConTextItems(self.files['lexical_kb'][1])
        assert items

class functional_test_tagItem(unittest.TestCase):
    def setUp(self):
        # create a sample image in memory

        self.items = {"targets":[ CI.create_ConTextItem([u"pulmonary embolism",
                        u"PULMONARY_EMBOLISM",
                        r"""pulmonary\s(artery )?(embol[a-z]+)""",""])],
                      "modifiers":[CI.create_ConTextItem(["no gross evidence of",
                        "PROBABLE_NEGATED_EXISTENCE,HEDGE_TERM","","forward"])]}
        self.ci0 = self.items['targets'][0]
        self.ci1 = self.items['modifiers'][0]

    def tearDown(self):
        self.items = 0
        self.ci0 = 0
        self.ci1 = 0
    def test_create_tagItem(self):
        ti = TI.create_tagItem(self.ci0,(20,30),"Brian Chapman",0)
        assert ti.span == (20,30)
    def test_limitCategoryScopeBackward(self):
        ti0 = TI.create_tagItem(self.ci0,(20,30),"Brian Chapman",0)
        ti1 = TI.create_tagItem(self.ci0,( 5,15),"Wendy Chapman",1)
        assert TI.lessthan(ti1,ti0)
        assert not TI.lessthan(ti0,ti1)
    def test_o1_encompasses_o2(self):

        ti0 = TI.create_tagItem(self.ci0,(20,25),"Brian Chapman",0)
        ti1 = TI.create_tagItem(self.ci0,( 5,30),"Wendy Chapman",1)
        assert TI.o1_encompasses_o2(ti1,ti0)
        assert not TI.o1_encompasses_o2(ti0,ti1)

    # add function to test DocumentGraph generation


class functional_test_ConTextMarkup(unittest.TestCase):
    def setUp(self):
        # create a sample image in memory


        self.su1 = u'kanso <Diagnosis>**diabetes**</Diagnosis> utesl\xf6t eller diabetes men inte s\xe4kert. Vi siktar p\xe5 en r\xf6ntgenkontroll. kan det vara nej panik\xe5ngesten\n?'
        self.su2 =  u'IMPRESSION: 1. LIMITED STUDY DEMONSTRATING NO GROSS EVIDENCE OF SIGNIFICANT PULMONARY EMBOLISM.'
        self.su3 = u'This is a sentence that does not end with a number. But this sentence ends with 1. So this should be recognized as a third sentence.'
        self.su4 = u'This is a sentence with a numeric value equal to 1.43 and should not be split into two parts.'
        self.items = {"targets":[ CI.create_ConTextItem([u"pulmonary embolism",
                                   u"PULMONARY_EMBOLISM",
                                   r"""pulmonary\s(artery )?(embol[a-z]+)""",
                                   ""]),
                                   ],
                       "modifiers":[CI.create_ConTextItem(["no gross evidence of",
                                     "PROBABLE_NEGATED_EXISTENCE",
                                     "",
                                     "forward"])]}



        self.ci0 = self.items['targets'][0]
        self.ci1 = self.items['modifiers'][0]
        self.ti0 = TI.create_tagItem(self.ci0,(20,25),"Brian Chapman",0)
        self.ti1 = TI.create_tagItem(self.ci0,( 5,30),"Wendy Chapman",1)
        self.markup = nx.DiGraph()
        self.markup.add_nodes_from([self.ti0,self.ti1])


    def tearDown(self):
        self.su1 = 0
        self.su2 = 0
        self.su3 = 0
        self.su4 = 0
        self.items = 0
        self.ci0 = 0
        self.ci1 = 0
        self.ti0 = 0
        self.ti1 = 0
        self.markup = 0
    def test_create_markup(self):
        assert self.markup

    def test_setRawText(self):
        self.markup = CM.setRawText(self.markup, self.su1)
        assert self.markup.graph["__rawText"] == self.su1
    def test_scrub_preserve_unicode(self):
        self.markup = CM.setRawText(self.markup, self.su1)
        self.markup = CM.cleanText(self.markup, stripNonAlphaNumeric=True)
        assert self.markup.graph["__text"].index(u'\xf6') == 40
    def test_scrub_text(self):
        self.markup = CM.setRawText(self.markup, self.su2)
        self.markup = CM.cleanText( self.markup, stripNonAlphaNumeric=True)
        assert self.markup.graph["__text"].rfind(u'.') == -1

    def test_prune_marks(self):
        markup_new = CM.prune_marks(self.markup)
        assert len(markup_new) == 1
        assert markup_new.nodes()[0].id == 1
    def test_mark_sentence(self):
        mu = CM.mark_sentence(self.su2,self.items)
        assert mu

class functional_test_ConTextDocument(unittest.TestCase):
    def setUp(self):
        # create a sample image in memory


        self.su1 = u'kanso <Diagnosis>**diabetes**</Diagnosis> utesl\xf6t eller diabetes men inte s\xe4kert. Vi siktar p\xe5 en r\xf6ntgenkontroll. kan det vara nej panik\xe5ngesten\n?'
        self.su2 =  u'IMPRESSION: 1. LIMITED STUDY DEMONSTRATING NO GROSS EVIDENCE OF SIGNIFICANT PULMONARY EMBOLISM.'
        self.su3 = u'This is a sentence that does not end with a number. But this sentence ends with 1. So this should be recognized as a third sentence.'
        self.su4 = u'This is a sentence with a numeric value equal to 1.43 and should not be split into two parts.'
        self.items = {"targets":[ CI.create_ConTextItem([u"pulmonary embolism",
                        u"PULMONARY_EMBOLISM",
                        r"""pulmonary\s(artery )?(embol[a-z]+)""",""])],
                       "modifiers":[CI.create_ConTextItem(["no gross evidence of",
                        "PROBABLE_NEGATED_EXISTENCE","","forward"])]}



        self.ci0 = self.items['targets'][0]
        self.ci1 = self.items['modifiers'][0]
        self.ti0 = TI.create_tagItem(self.ci0,(20,25),"Brian Chapman",0)
        self.ti1 = TI.create_tagItem(self.ci0,( 5,30),"Wendy Chapman",1)
        self.markup = nx.DiGraph()
        self.markup.add_nodes_from([self.ti0,self.ti1])
        self.cd = CD.ConTextDocument()



    def tearDown(self):
        self.su1 = 0
        self.su2 = 0
        self.su3 = 0
        self.su4 = 0
        self.items = 0
        self.ci0 = 0
        self.ci1 = 0
        self.ti0 = 0
        self.ti1 = 0
        self.markup = 0
        self.cd = 0

#


    def test_create_ConTextDocument(self):
        cd = CD.ConTextDocument()
        assert cd.graph["__documentGraph"] == None

    def test_TextBlob1(self):
        blob = TextBlob(self.su1)
        assert len(blob.sentences) == 3


    def test_TextBlob3(self):
        blob = TextBlob(self.su3)
        assert len(blob.sentences) == 3

    def test_TextBlob4(self):
        blob = TextBlob(self.su4)
        assert len(blob.sentences) == 1

    def test_insertSection(self):
        cd2 = CD.insertSection(self.cd,
                               "report",
                               setToParent=True,
                               setToRoot = True)
        assert CD.getCurrentparent(cd2) == "report"


def run():
    pass
