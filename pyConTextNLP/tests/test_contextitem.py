import unittest
import pyConTextNLP.itemData as itemData

class ConTextItemTest(unittest.TestCase):
    def setUp(self):
        # create a sample image in memory


        self.items = [ ["pulmonary embolism",
                        "PULMONARY_EMBOLISM",
                        r"""pulmonary\s(artery )?(embol[a-z]+)""",
                        ""],
                       ["no gross evidence of",
                        "PROBABLE_NEGATED_EXISTENCE",
                        "",
                        "forward"]]

    def tearDown(self):

        self.items = []

    #def testSource(self):
        #assert self.context.__file__ == 'pyConTextGraph.pyc'
    def test_itemData_from_yaml(self):
        f = "https://github.com/chapmanbe/pyConTextNLP/blob/master/KB/domain_kb_test.yml"
        assert True 
        #assert itemData.itemData_from_tsv(f)


    def test_instantiate_contextItem0(self):
        for item in self.items:
            assert itemData.contextItem(item)


    def test_contextItem_rule(self):
        cti = itemData.contextItem(self.items[1])

        assert cti.getRule() == "forward"


    def test_contextItem_literal(self):
        cti = itemData.contextItem(self.items[0])

        assert cti.getLiteral() == "pulmonary embolism"


    def test_contextItem_category(self):
        cti = itemData.contextItem(self.items[1])
        assert cti.getCategory() == ["probable_negated_existence"]

    def test_contextItem_isa(self):
        cti = itemData.contextItem(self.items[0])
        assert cti.isA("pulmonary_embolism")


    def test_contextItem_isa1(self):
        cti = itemData.contextItem(self.items[0])
        assert cti.isA("PULMONARY_EMBOLISM")


    def test_contextItem_isa2(self):
        cti = itemData.contextItem(self.items[1])
        assert cti.isA("PROBABLE_NEGATED_EXISTENCE")


    def test_contextItem_getRE(self):
        cti = itemData.contextItem(self.items[1])
        assert cti.getRE() == r'\b%s\b'%self.items[1][0]


    def test_contextItem_getRE1(self):
        cti = itemData.contextItem(self.items[0])
        assert cti.getRE() == r"""pulmonary\s(artery )?(embol[a-z]+)"""


def run():
    pass
    
