import unittest
import pyConTextNLP.functional.tagObjects as tagObjects
import pyConTextNLP.functional.ConTextMarkup as ConTextMarkup
import pyConTextNLP.functional.ConTextDocument as ConTextDocument
import pyConTextNLP.helpers as helpers
from textblob import TextBlob

class functional_test(unittest.TestCase):
    def setUp(self):
        # create a sample image in memory
        self.context = pyConText.ConTextMarkup()
        self.splitter = helpers.sentenceSplitter()


        self.su1 = u'kanso <Diagnosis>**diabetes**</Diagnosis> utesl\xf6t eller diabetes men inte s\xe4kert. Vi siktar p\xe5 en r\xf6ntgenkontroll. kan det vara nej panik\xe5ngesten\n?'
        self.su2 =  u'IMPRESSION: 1. LIMITED STUDY DEMONSTRATING NO GROSS EVIDENCE OF SIGNIFICANT PULMONARY EMBOLISM.'
        self.su3 = u'This is a sentence that does not end with a number. But this sentence ends with 1. So this should be recognized as a third sentence.'
        self.su4 = u'This is a sentence with a numeric value equal to 1.43 and should not be split into two parts.'
        self.items = [ [u"pulmonary embolism",u"PULMONARY_EMBOLISM",ur"""pulmonary\s(artery )?(embol[a-z]+)""",""],["no gross evidence of","PROBABLE_NEGATED_EXISTENCE","","forward"]]

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

    # add function to test DocumentGraph generation  
def run():
    pass
    
