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
import platform
import collections


class ConTextItem(collections.namedtuple('ConTextItem',
                  ['literal', 'category', 're', 'rule'])):
    def __str__(self):
        return """literal<<{0}>>; category<<{1}>>; re<<{2}>>; rule<<{3}>>""".format(
                        self.literal,
                        get_ConTextItem_category_string(self),
                        self.re,
                        self.rule)


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

if platform.python_version_tuple()[0] == '2':

    import unicodecsv as csv
    import urllib2

    def get_fileobj(csvFile):
        p = urllib2.urlparse.urlparse(csvFile)
        if not p.scheme:
            csvFile = "file://"+csvFile
        f0 = urllib2.urlopen(csvFile, 'rU')
        return csv.reader(f0, encoding='utf-8', delimiter="\t"), f0

else:
    import csv
    import urllib.request
    import urllib.error
    import urllib.parse
    from io import StringIO

    def get_fileobj(csvFile):
        p = urllib.parse.urlparse(csvFile)
        if not p.scheme:
            csvFile = "file://"+csvFile
        f0 = urllib.request.urlopen(csvFile, data=None)
        return csv.reader(StringIO(f0.read().decode(), newline=None), delimiter="\t" ), f0

def readConTextItems(csvFile,
                     encoding='utf-8',
                     headerRows=1,
                     literalColumn=0,
                     categoryColumn=1,
                     regexColumn=2,
                     ruleColumn=3):
    """
    takes a CSV file of itemdata rules and creates a list of
        ConTextItem instances.
    csvFile: name of file to read items from
    encoding: unicode enocidng to use; default = 'utf-8'
    headerRows: number of header rows in file; default = 1
    literalColumn: column from which to read the literal; default = 0
    categoryColumn: column from which to read the category; default = 1
    regexColumn: column from which to read the regular expression: default = 2
    ruleColumn: column from which to read the rule; default = 3
    """
    items = []
    header = []
    reader, f0 = get_fileobj(csvFile)
    # reader = csv.reader(open(csvFile, 'rU'))
    # first grab number of specified header rows
    for i in range(headerRows):
        row = next(reader)
        header.append(row)
    # now grab each itemData
    for row in reader:
        tmp = [row[literalColumn], row[categoryColumn],
               row[regexColumn], row[ruleColumn]]
        tmp[2] = r"{0}".format(tmp[2])
        # convert the regular expression string into a raw StringIO
        item = create_ConTextItem(tmp)
        items.append(item)
    f0.close()
    return items, header


def writeConTextItems(items, fname):
    """
    Write the ConTextItems as a tab delimited file to the file specified
    in fname
    """
    with open(fname, 'w') as f0:
        f0.write("Lex\tType\tRegex\tRule\n")
        for i in items:
            f0.write("%s\t%s\t%s\t%s\n" % (i.literal,
                                           ",".join(i.category),
                                           i.re,
                                           i.rule))
