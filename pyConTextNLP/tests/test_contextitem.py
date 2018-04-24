import pyConTextNLP.itemData as itemData
import pytest

@pytest.fixture(scope="module")
def items():

    return [ ["pulmonary embolism",
              "PULMONARY_EMBOLISM",
             r"""pulmonary\s(artery )?(embol[a-z]+)""",
              ""],
             ["no gross evidence of",
              "PROBABLE_NEGATED_EXISTENCE",
              "",
              "forward"]]

def test_instantiate_contextItem0(items):
    for item in items:
        assert itemData.contextItem(item)


def test_contextItem_rule(items):
    cti = itemData.contextItem(items[1])

    assert cti.getRule() == "forward"


def test_contextItem_literal(items):
    cti = itemData.contextItem(items[0])

    assert cti.getLiteral() == "pulmonary embolism"


def test_contextItem_category(items):
    cti = itemData.contextItem(items[1])
    assert cti.getCategory() == ["probable_negated_existence"]

def test_contextItem_isa(items):
    cti = itemData.contextItem(items[0])
    assert cti.isA("pulmonary_embolism")


def test_contextItem_isa1(items):
    cti = itemData.contextItem(items[0])
    assert cti.isA("PULMONARY_EMBOLISM")


def test_contextItem_isa2(items):
    cti = itemData.contextItem(items[1])
    assert cti.isA("PROBABLE_NEGATED_EXISTENCE")


def test_contextItem_getRE(items):
    cti = itemData.contextItem(items[1])
    assert cti.getRE() == r'\b%s\b'%items[1][0]


def test_contextItem_getRE1(items):
    cti = itemData.contextItem(items[0])
    assert cti.getRE() == r"""pulmonary\s(artery )?(embol[a-z]+)"""

