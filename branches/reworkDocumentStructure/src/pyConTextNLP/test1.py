import unittest
import itemData
import pyConTextGraph as pyConText
import helpers
class pyConTextNLP_test(unittest.TestCase):
    def setUp(self):
        # create a sample image in memory
        self.context = pyConText.ConTextMarkup()
        self.splitter = helpers.sentenceSplitter()

        self.su1 = u'kanso <Diagnosis>**diabetes**</Diagnosis> utesl\xf6t eller diabetes men inte s\xe4kert. Vi siktar p\xe5 en r\xf6ntgenkontroll. kan det vara nej panik\xe5ngesten\n?'
        self.su2 =  u'IMPRESSION: 1. LIMITED STUDY DEMONSTRATING NO GROSS EVIDENCE OF SIGNIFICANT PULMONARY EMBOLISM.'
        self.su3 = u'This is a sentence that does not end with a number. But this sentence ends with 1.'
        self.items = [ [u"pulmonary embolism",u"PULMONARY_EMBOLISM",ur"""pulmonary\s(artery )?(embol[a-z]+)""",""],["no gross evidence of","PROBABLE_NEGATED_EXISTENCE","","forward"]]
        self.itemData = itemData.itemData()
        for i in self.items:
            cit = itemData.contextItem

    def tearDown(self):
        self.context = 0
        self.splitter = 0
        self.su1 = 0
    #def testSource(self):
        #assert self.context.__file__ == 'pyConTextGraph.pyc'
    def test_setRawText(self):
        self.context.setRawText(self.su1)
        assert self.context.getRawText() == self.su1
    def test_scrub_preserve_unicode(self):
        self.context.setRawText(self.su1)
        self.context.cleanText(stripNonAlphaNumeric=True)
        assert self.context.getText().index(u'\xf6') == 40
    def test_scrub_text(self):
        self.context.setRawText(self.su2)
        self.context.cleanText(stripNonAlphaNumeric=True)
        assert self.context.getText().rfind(u'.') == -1
    def test_createSentenceSplitter(self):
        assert helpers.sentenceSplitter()
    def test_getExceptionTerms(self):
        assert self.splitter.getExceptionTerms()
    def test_addExceptionTermsWithoutCaseVariants(self):
        self.splitter.addExceptionTerms("D.D.S.", "D.O.")
        assert ("D.O." in self.splitter.getExceptionTerms())
        assert ("d.o." not in self.splitter.getExceptionTerms())
    def test_addExceptionTermsWithCaseVariants(self):
        self.splitter.addExceptionTerms("D.D.S.", "D.O.",addCaseVariants=True)
        assert ("d.o." in self.splitter.getExceptionTerms())
    def test_deleteExceptionTermsWithoutCaseVariants(self):
        self.splitter.deleteExceptionTerms("M.D.")
        assert ("M.D." not in self.splitter.getExceptionTerms())
        assert ("m.d." in self.splitter.getExceptionTerms())
    def test_instantiate_contextItem(self):
        cit1 = itemData.contextItem(self.items[0])
        assert cit1
    def test_instantiate_itemData(self):
        cit1 = itemData.contextItem(self.items[0])
        it1 = itemData.itemData()
        it1.append(cit1)
        assert it1
    def test_tokenDistance(self):
        assert False
    def test_sentenceSplitter1(self):
        """test whether we properly capture text that terminates without a recognized sentence termination"""
        splitter = helpers.sentenceSplitter()
        sentences = splitter.splitSentences(self.su3)
        assert len(sentences) == 2
    # add function to test DocumentGraph generation  
def run():
    pass
    
