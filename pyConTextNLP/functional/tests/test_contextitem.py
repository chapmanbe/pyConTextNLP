import pyConTextNLP.functional.ConTextItem as CI
import pytest

@pytest.fixture(scope="module")
def items():

    return [ ["pulmonary embolism",
              ["PULMONARY_EMBOLISM"],
             r"""pulmonary\s(artery )?(embol[a-z]+)""",
              ""],
             ["no gross evidence of",
             [ "PROBABLE_NEGATED_EXISTENCE"],
              "",
              "forward"]]

def test_instantiate_ConTextItem0(items):
    for item in items:
        assert CI.ConTextItem(*item)


def test_ConTextItem_rule(items):
    cti = CI.ConTextItem(*(items[1]))

    assert cti.rule == "forward"


def test_ConTextItem_literal(items):
    cti = CI.ConTextItem(*(items[0]))

    assert cti.literal == "pulmonary embolism"


def test_ConTextItem_category(items):
    cti = CI.ConTextItem(*(items[1]))
    assert cti.category == ["probable_negated_existence"]

def test_ConTextItem_isa(items):
    cti = CI.ConTextItem(*(items[0]))
    assert CI.isA(cti, "pulmonary_embolism")


def test_ConTextItem_isa1(items):
    cti = CI.ConTextItem(*(items[0]))
    assert CI.isA(cti, "PULMONARY_EMBOLISM")


def test_ConTextItem_isa2(items):
    cti = CI.ConTextItem(*(items[1]))
    assert CI.isA(cti, "PROBABLE_NEGATED_EXISTENCE")


def test_ConTextItem_getRE(items):
    cti = CI.ConTextItem(*(items[1]))
    assert cti.re == r'\b%s\b'%items[1][0]


def test_ConTextItem_getRE1(items):
    cti = CI.ConTextItem(*(items[0]))
    assert cti.re == r"""pulmonary\s(artery )?(embol[a-z]+)"""

