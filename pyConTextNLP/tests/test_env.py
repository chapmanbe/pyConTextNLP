def test_yaml():
    import yaml
    assert yaml

def test_networkx():
    import networkx as nx
    assert nx

def test_networkx_v2x():
    import networkx as nx
    assert nx.__version__[0] == '2'
