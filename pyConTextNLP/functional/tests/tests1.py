import pyConTextNLP.functional.ConTextItem as CI

def test_create_ConTextItem_targets(items):
    ci = CI.create_ConTextItem(items['targets'][0])
    assert ci.re == items['targets'][0][2]
    assert ci.category == (items['targets'][0][1].lower().strip(),)

def test_create_ConTextItem_modifiers(items):
    ci = CI.create_ConTextItem(items['modifiers'][0])
    assert ci.re == r"\b%s\b"%items['modifiers'][0][0].lower().strip()
    assert len(ci.category) == 2

def test_isA(items):
    ci = CI.create_ConTextItem(items["modifiers"][0])
    assert CI.isA(ci,"HEART_DISEASE") == False
    assert CI.isA(ci,"HEDGE_TERM") == True


def test_test_rule(items):
    ci = CI.create_ConTextItem(items["modifiers"][0])
    assert CI.test_rule(ci,"Forward") == True
    assert CI.test_rule(ci,"forward") == True
    assert CI.test_rule(ci,"bidirection") == False


def test_read_ConTextItem0(files):
    items = CI.get_items(files['lexical_kb'][0])
    assert items

def test_read_ConTextItem1(files):
    items = CI.get_items(files['lexical_kb'][1])
    assert items


