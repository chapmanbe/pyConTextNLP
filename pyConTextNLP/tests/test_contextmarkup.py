from pyConTextNLP.ConTextMarkup import ConTextMarkup
import pytest

@pytest.fixture(scope="module")
def sent1():
    return 'kanso <Diagnosis>**diabetes**</Diagnosis> utesl\xf6t eller diabetes men inte s\xe4kert. Vi siktar p\xe5 en r\xf6ntgenkontroll. kan det vara nej panik\xe5ngesten\n?'

@pytest.fixture(scope="module")
def sent2():
    return 'IMPRESSION: 1. LIMITED STUDY DEMONSTRATING NO GROSS EVIDENCE OF SIGNIFICANT PULMONARY EMBOLISM.'
@pytest.fixture(scope="module")
def sent3():
    return 'This is a sentence that does not end with a number. But this sentence ends with 1. So this should be recognized as a third sentence.'

@pytest.fixture(scope="module")
def sent4():
    return 'This is a sentence with a numeric value equal to 1.43 and should not be split into two parts.'

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

def test_setRawText1(sent1):
    context = ConTextMarkup()
    context.setRawText(sent1)
    assert context.getRawText() == sent1

def test_scrub_preserve_unicode(sent1):
    context = ConTextMarkup()
    context.setRawText(sent1)
    context.cleanText(stripNonAlphaNumeric=True)
    assert context.getText().index(u'\xf6') == 40

def test_scrub_text(sent2):
    context = ConTextMarkup()
    context.setRawText(sent2)
    context.cleanText(stripNonAlphaNumeric=True)
    assert context.getText().rfind(u'.') == -1
