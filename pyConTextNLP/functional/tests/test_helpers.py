import pyConTextNLP.helpers as helpers
import pytest

@pytest.fixture(scope="module")
def splitter():
    return helpers.sentenceSplitter()


def test_createSentenceSplitter():
        assert helpers.sentenceSplitter()


def test_getExceptionTerms(splitter):
    assert splitter.getExceptionTerms()


def test_addExceptionTermsWithoutCaseVariants(splitter):
    splitter.addExceptionTerms("D.D.S.", "D.O.")
    assert ("D.O." in splitter.getExceptionTerms())
    #assert ("d.o." in splitter.getExceptionTerms())


def test_addExceptionTermsWithCaseVariants(splitter):
    splitter.addExceptionTerms("D.D.S.", "D.O.",addCaseVariants=True)
    assert ("d.o." in splitter.getExceptionTerms())
   

def test_deleteExceptionTermsWithoutCaseVariants(splitter):
    splitter.deleteExceptionTerms("M.D.")
    assert ("M.D." not in splitter.getExceptionTerms())
    assert ("m.d." in splitter.getExceptionTerms())
