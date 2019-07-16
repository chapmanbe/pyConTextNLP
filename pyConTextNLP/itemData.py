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
A module defining the contextItem class.
"""
import os

import yaml
import urllib
import csv
from io import StringIO

def _get_fileobj(_file):
    p = urllib.parse.urlparse(_file)
    if not p.scheme:
        csvFile = "file://" + _file
    f0 = urllib.urlopen(csvFile, 'rU')
    return csv.reader(StringIO(f0.read().decode(), newline=None), delimiter="\t"), f0


def get_items(file_str):
    file_name = file_str.lower()
    if file_name.endswith(".csv") or file_name.endswith(".tsv") or file_name.endswith(".yml"):
        if 'http' not in file_str.lower():
            pwd = os.getcwd()
            if pwd not in file_str:
                file_str = os.path.join(pwd, file_str)
            if not os.path.exists(file_str):
                return contextItem()
        if file_name.endswith('csv') or file_name.endswith('tsv'):
            return instantiateFromCSVtoitemData(file_str)
        elif file_name.endswith('yml'):
            return instantiateFromYMLtoitemData(file_str)
        else:
            return contextItem()
    elif "Comments:" in file_str:
        return instantiateFromYMLStr(file_str)
    elif ',' in file_str:
        return instantiateFromCSVStr(file_str, ',')
    elif '\t' in file_str:
        return instantiateFromCSVStr(file_str, '\t')
    else:
        print(
            "This input format is not supported. It can be either a path of csv, tsv or yaml file, or a string of corresponding file content.")


class contextItem(object):

    def __init__(self, args):
        self.__literal = args[0]
        cs = args[1].split(",")
        self.__category = []
        for c in cs:
            self.__category.append(c.lower().strip())
        self.__re = r"%s" % args[2]  # I need to figure out how to read this raw string in properly
        self.__rule = args[3].lower()

        # generate regex from literal if no regex provided
        if not self.__re:
            self.__re = r"\b{}\b".format(self.__literal)

    def getLiteral(self):
        """return the literal associated with this item"""
        return self.__literal

    def getCategory(self):
        """return the list of categories associated with this item"""
        return self.__category[:]

    def categoryString(self):
        """return the categories as a string delimited by '_'"""
        return '_'.join(self.__category)

    def isA(self, testCategory):
        """test whether testCategory is one of the categories associated with self"""
        try:
            return testCategory.lower().strip() in self.__category
        except:
            for tc in testCategory:
                if (tc.lower().strip() in self.__category):
                    return True
            return False

    def getRE(self):
        return self.__re

    def getRule(self):
        return self.__rule

    def __str__(self):
        txt = """literal<<{0}>>; category<<{1}>>; re<<{2}>>; rule<<{3}>>""".format(
            self.__literal, self.__category, self.__re, self.__rule)
        return txt

    def __repr__(self):
        return self.__str__()


def instantiateFromCSVStr(content, splitter):
    reader = csv.reader(content.split('\n'), delimiter=splitter)
    items = contextItem()
    for row in reader:
        # print(row)
        tmp = read_row(row)
        if tmp is None:
            continue
        # tmp = [row[literalColumn], row[categoryColumn],
        # 	   row[regexColumn], row[ruleColumn]]
        # tmp[2] = r"{0}".format(tmp[2])  # convert the regular expression string into a raw string
        item = contextItem(tmp)
        items.append(item)
    return items


def instantiateFromYMLStr(content):
    context_items = [contextItem((d["Lex"],
                                  d["Type"],
                                  r"%s" % d["Regex"],
                                  d["Direction"])) for d in yaml.safe_load_all(content)]
    return context_items


def instantiateFromYMLtoitemData(_file):
    def get_fileobj(_file):
        if not urllib.parse.urlparse(_file).scheme:
            _file = "file://" + _file
        return urllib.request.urlopen(_file, data=None)

    f0 = get_fileobj(_file)
    context_items = [contextItem((d["Lex"],
                                  d["Type"],
                                  r"%s" % d["Regex"],
                                  d["Direction"])) for d in yaml.safe_load_all(f0)]
    return context_items


def instantiateFromCSVtoitemData(csvFile, encoding='utf-8', headerRows=1, literalColumn=0, categoryColumn=1,
                                 regexColumn=2, ruleColumn=3):
    items = contextItem()  # itemData to be returned to the user
    header = []
    reader, f0 = _get_fileobj(csvFile)
    # reader = csv.reader(open(csvFile, 'rU'))
    # first grab numbe rof specified header rows
    for i in range(headerRows):
        row = next(reader)
        header.append(row)
    # now grab each itemData
    for row in reader:
        # print(row)
        tmp = read_row(row)
        if tmp is None:
            continue
        # tmp = [row[literalColumn], row[categoryColumn],
        # 	   row[regexColumn], row[ruleColumn]]
        # tmp[2] = r"{0}".format(tmp[2])  # convert the regular expression string into a raw string
        item = contextItem(tmp)
        items.append(item)
    f0.close()
    return items


def read_row(row):
    tmp = []
    if len(row) < 2 or row[0].startswith('#'):
        return None
    tmp.extend([row[0], row[1]])
    if len(row) == 3:
        tmp.extend([r"{0}".format(row[2]), ''])
    elif len(row) == 2:
        tmp.extend(['', ''])
    else:
        tmp.extend([row[2], row[3]])
    return tmp
