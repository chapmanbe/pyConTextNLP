# Copyright 2010 Brian E. Chapman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
ConTextItem---DOCSTRING
"""
import collections
import csv
import urllib.request
import urllib.error
import urllib.parse
from io import StringIO
import yaml



class ConTextItem(collections.namedtuple('ConTextItem',
                  ['literal', 'category', 're', 'rule'])):
    def __str__(self):
        return """literal<<{0}>>; category<<{1}>>; re<<{2}>>; rule<<{3}>>""".format(
                        self.literal,
                        get_ConTextItem_category_string(self),
                        self.re,
                        self.rule)


#   def __new__(ConTextItem,l,c,rgx, rl, *args, **kwargs):
#       _l = l.lower().strip()
#       return super().__new__(ConTextItem, _l, c, _assign_regex(_l, rgx), rl)
def _get_categories(cats):
    if "," in cats:
        return tuple([c.lower().strip() for c in cats.split(",")])
    else:
        return (cats.lower().strip(), )


def _assign_regex(r1, r2):
    if r2:
        return r2.lower().strip()
    else:
        return r'\b%s\b'%r1.lower().strip()


def get_ConTextItem_category_string(ci):
    return "_".join(ci.category)


def create_ConTextItem(args):
    return ConTextItem(literal=args[0].lower().strip(),
                       category=_get_categories(args[1]),
                       re=_assign_regex(args[0], args[2]),
                       rule=args[3]
                       )


def test_rule(ci, rule_query):
    return rule_query.lower() in ci.rule


def isA(citem, testCategory):
    """
    test whether testCategory is one of the categories
    associated with citem
    """
    try:
        return testCategory.lower().strip() in citem.category
    except:
        for tc in testCategory:
            if tc.lower().strip() in citem.category:
                return True
        return False


def ConTextItem2string(ci):
    return ci.__unicode__()


def get_fileobj(csvFile):
    p = urllib.parse.urlparse(csvFile)
    if not p.scheme:
        csvFile = "file://"+csvFile
    f0 = urllib.request.urlopen(csvFile, data=None)
    return csv.reader(StringIO(f0.read().decode(), newline=None), delimiter="\t" ), f0




def _get_fileobj(_file):
    if not urllib.parse.urlparse(_file).scheme:
        _file = "file://"+_file
    return urllib.request.urlopen(_file, data=None)

def get_items(_file):
    f0 = _get_fileobj(_file)
    context_items =  [ConTextItem(literal=d["Lex"],
                                   category=d["Type"],
                                   re=r"%s"%d["Regex"],
                                   rule=d["Direction"]) for d in yaml.load_all(f0)]
    f0.close()
    return context_items



