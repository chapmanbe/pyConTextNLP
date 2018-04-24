#!/usr/bin/env python
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
"""processReports.py is a program that uses pyConTextNLP to process reports
in a Microsfot Access database.

By default the database has a table named 'test_MyReports' with a field named 'report'.
These values can be be specified through the command line options.

The code is currently written to support either a Microsoft Access database or a SQLite database.

Much of the class constructor is dedicated to creating tables in the database for writing the results.
A number of tables are created including a table containing the schema used, the arguments specified
on the command line and the results.

The heart of the code is in analyzeReport where the pyConTextNLP algorithm is applied to an individual report.

"""
#import sys
import argparse
import pyConTextNLP
import pyConTextNLP.pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData
import pyConTextNLP.helpers as helpers
import getpass
import time
import xml.dom.minidom as minidom
import sqlite3 as sqlite
import os
import sys
#import ast

def instantiateSchema(values,rule):
    """evaluates rule by substituting values into rule and evaluating the resulting literal.
    For security the ast.literal_eval() method is used.
    """
    r = rule
    for k in values.keys():
        r = r.replace(k,values[k].__str__())
    #return ast.literal_eval(r)
    return eval(r)

def assignSchema(values,rules):
    for k in rules.keys():
        if( instantiateSchema(values,rules[k][1]) ):
            return k

def modifies(g,n,modifiers):
    """Tests whether any of the modifiers of node n are in any of the categories listed in 'modifiers'"""
    pred = g.predecessors(n)
    if( not pred ):
        return False
    #pcats = [p.getCategory().lower() for p in pred]
    pcats = []
    for p in pred:
        pcats.extend(p.getCategory())
    return bool(set(pcats).intersection([m.lower() for m in modifiers]))
def matchedModifiers(g,n,modifiers):
    """returns the set of predecessors of node 'n' that are of a category contained in 'modifiers'"""
    pred = g.predecessors(n)
    if( not pred ):
        return False
    #pcats = [p.getCategory().lower() for p in pred]
    pcats = []
    for p in pred:
        pcats.extend(p.getCategory())
    print pcats
    print [m.lower() for m in modifiers]
    print set(pcats).intersection([m.lower() for m in modifiers])
    return set(pcats).intersection([m.lower() for m in modifiers])

def returnMatchedModifiers(g,n,modifiers):
    pred = g.predecessors(n)
    if( not pred ):
        return []
    mods = [m.lower() for m in modifiers]
    mmods = [p for p in pred if p.isA(mods)]
    return mmods
def getSeverity(g,t,severityRule):
    if(not t.isA(severityRule[0]) ):
        return []
    smods = returnMatchedModifiers(g,t,severityRule[1])
    if( smods ):
        severityResults = []
        for m in smods:
            mgd = m.getMatchedGroupDictionary()
            val = mgd.get('value')
            units = mgd.get('unit')
            phrase = m.getPhrase()
        severityResults.append((phrase,val,units))
        return severityResults
    else:
        return []
def anatomyRecategorize(g,t,categoryRule):
    """create a new category based on categoryRule"""
    if( not t.isA( categoryRule[0] ) ):
        return 
    mods = g.predecessors(t)

    if( mods ):
        mmods = matchedModifiers(g,t,categoryRule[1])
        if( mmods ):
            newCategory = []
            for m in mmods:
                nc = "_".join([m.lower(),categoryRule[0]])
                newCategory.append(nc)
            print "newCategory=",newCategory
            t.replaceCategory(categoryRule[0],newCategory)
            print "modified Category is",t.getCategory()
def genericClassifier(g,t,rule):
    """based on the modifiers of the target 't' and the provide rule in 'rule' classify the target node"""
    mods = g.predecessors(t)
    if( not mods ):
        return rule["DEFAULT"]
    for r in rule["RULES"]:
        if( modifies(g,t,r[1]) ):
            return r[0]
    return rule["DEFAULT"]
class criticalFinder(object):
    """This is the class definition that will contain the majority of processing
    algorithms for criticalFinder.

    The constructor takes as an argument the name of an SQLite/Access database containing
    the relevant information.
    """
    def __init__(self, schema='',rules='',rid='',column='',table='',result_label='',mode='sqlite',dbname='',
                 lexical_kb = None, domain_kb = None, debug=False):
        """create an instance of a criticalFinder object associated with the SQLite
        database.
        dbname: name of SQLite database
        """
        if( lexical_kb == None ):
            lexical_kb = []
        if( domain_kb == None ):
            domain_kb = []

        self.lexical_kb = lexical_kb
        self.domain_kb = domain_kb
        if( not schema ):
            print "You must specify a schema file"
            sys.exit(0)
        try:
            self.readSchema(schema)
        except Exception, error:
            print "The schema is not in the correct format",error
            sys.exit(0)
        if( not rules ):
            print "you must specify a rules file"
            sys.exit(0)
        try:
            self.readRules(rules)
        except Exception, error:
            print "The rules are not in the correct format", error
            sys.exit(0)
        # Define queries to select data from the SQLite database
        # this gets the reports we will process
        self.rid = rid
        self.column = column
        self.table = table
        self.result_label = result_label
        self.query1 = '''SELECT %s,%s FROM %s'''%(self.rid,self.column,self.table)
        print self.query1
        self.mode = mode
        self.dbname = dbname
        self.getDBConnection(self.dbname)

        # get reports to process
        self.cursor.execute(self.query1)
        self.reports = self.cursor.fetchall()

        print "number of reports to process",len(self.reports)
        # Create the pyConTextNLP ConTextDocument. This is the container for all the markups
        self.document = pyConText.ConTextDocument()

        self.modifiers = itemData.itemData()
        self.targets = itemData.itemData()
        for kb in lexical_kb:
            self.modifiers.extend( itemData.instantiateFromCSVtoitemData(kb) )
        for kb in domain_kb:
            self.targets.extend( itemData.instantiateFromCSVtoitemData(kb) )


        self.debug = debug
        if( self.debug ):
            print "debug set to True"
            tmp = os.path.splitext(self.dbname)
            self.debugDir = tmp[0]+"_debug_dir"
            if( not os.path.exists(self.debugDir) ):
                os.mkdir(self.debugDir)
        else:
            self.debugDir = ''
    def readRules(self,fname):
        """read the sentence level rules"""
        f0 = file(fname,"r")
        data = f0.readlines()
        self.class_rules = {}
        self.category_rules = []
        self.severity_rules = []
        for d in data:
            tmp = d.strip().split(",")
            if( not tmp[0][0] == "#" ): # # comment character
                if( tmp[0] == "@CLASSIFICATION_RULE" ):
                    r = self.class_rules.get(tmp[1],{"LABEL":"","DEFAULT":"","RULES":[]})
                    value = int(tmp[3])
                    if(tmp[2] == 'DEFAULT'):
                        r["DEFAULT"] = value
                    elif(tmp[2] == 'RULE'):
                        rcs = []
                        for rc in tmp[4:]:
                            rcs.append(rc)
                        r["RULES"].append((value,rcs))
                    self.class_rules[tmp[1]] = r
                elif( tmp[0] == "@CATEGORY_RULE"):
                    self.category_rules.append((tmp[1],[r for r in tmp[2:]]))
                elif( tmp[0] == "@SEVERITY_RULE"):
                    self.severity_rules.append((tmp[1],[r for r in tmp[2:]]))
        self.classification_schema += "\nCLASSIFICATION_RULES\n"
        for r in self.class_rules.keys():
            self.classification_schema += "%s %s\n"%(r,str(self.class_rules[r]))
        self.classification_schema += "\nCATEGORY_RULES\n"
        for cr in self.category_rules:
            self.classification_schema += "%s\n"%str(cr)
        self.classification_schema += "\nSEVERITY_RULES\n"
        for sr in self.severity_rules:
            self.classification_schema += "%s\n"%str(sr)


    def readSchema(self,fname):
        """read the schema and schema classifier functionality"""
        fo = file(fname,"r")
        self.schema = {}
        tmp = fo.readlines()
        for t in tmp:
            t = t.strip().split(",")
            if( t[0][0] != "#" ):
                self.schema[int(t[0])]=(t[1],t[2])
        self.classification_schema = ""
        for k in self.schema.keys():
            self.classification_schema += "%d: %s: %s\n"%(k,self.schema[k][0],self.schema[k][1])
    def _getLastRowID(self):
        if( self.mode == 'access' ):
            self.cursor.execute("""SELECT @@IDENTITY AS identity""")
            tmp = self.cursor.fetchone()
            return tmp[0]
        elif( self.mode == 'sqlite' ):
            return self.cursor.lastrowid
    def _getDBConnectionAccess(self,dbname):
        import pyodbc
        self.conn=pyodbc.connect("DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s"%dbname)
    def _getDBConnectionSQLite(self,dbname):
        self.conn=sqlite.connect(dbname)
    def getDBConnection(self,dbname):
        if( self.mode == 'access' ):
            self._getDBConnectionAccess(dbname)
        else:
            self._getDBConnectionSQLite(dbname)
        self.cursor = self.conn.cursor()

    def _createTablesAccess(self):
        try:
            self.cursor.execute("""create table run_args (rowid AUTOINCREMENT,
                                                          run_date text,
                                                          label text,
                                                          args text,
                                                          PRIMARY KEY(rowid))""")
        except:
            print "run_args table seems to already exist"
        try:
            self.cursor.execute("""CREATE TABLE class_schema (rowid AUTOINCREMENT,
                                                              schema text,
                                                              PRIMARY KEY(rowid))""")
        except:
            print "class_schema table seems to exist"
        try:
            self.cursor.execute(
                    """CREATE TABLE pyConTextNLP_results
                       (rowid AUTOINCREMENT, 
                        report_number int, 
                        run_args int, 
                        schema int,
			target_category text,
                        classification int, 
                        most_positive_target text,
                        PRIMARY KEY(rowid),
                        FOREIGN KEY (run_args) REFERENCES run_args(rowid),
                        FOREIGN KEY (schema) REFERENCES class_schema(rowid))""")

        except Exception,error:
            print error
            print "pyconTextNLP_results table seems to exist"
        try:
            self.cursor.execute(
                    """CREATE TABLE pyConTextNLP_severity
                        (rowid AUTOINCREMENT,
                        result int,
                        phrase text,
                        svalue text,
                        units text,
                        PRIMARY KEY(rowid),
                        FOREIGN KEY (result) REFERENCES pyConTextNLP_results(rowid))""")
        except Exception, error:
            print error
            print "pyConTextNLP_severity table seems to exist"
        
    def _createTablesSQLite(self):
        self.cursor.execute("""create table if not exists run_args (run_date text,
                                                                    label text,
                                                                    args text)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS class_schema (schema text)""")

        self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS pyConTextNLP_results
                    (report_number int, 
                    run_args int, 
                    schema int,
                    target_category text,
                    classification int, 
                    most_positive_target text,
                    FOREIGN KEY (run_args) REFERENCES run_args(rowid),
                    FOREIGN KEY (schema) REFERENCES class_schema(rowid))""")

        self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS pyConTextNLP_severity
                    (result int,
                    phrase text,
                    svalue text,
                    units text,
                    FOREIGN KEY (result) REFERENCES pyConTextNLP_results(rowid))""")

    def createTables(self):
            if( self.mode == "access" ):
                self._createTablesAccess()
            elif( self.mode == "sqlite" ):
                self._createTablesSQLite()

    def initializeOutput(self): #rfile,lfile,dfile):
        """Provides run specific information for XML output file"""
        self.outString  =u"""<?xml version="1.0"?>\n"""
        self.outString +=u"""<args>\n"""
        self.outString +=u"""<pyConTextNLPVersion> %s </pyConTextNLPVersion>\n"""%pyConTextNLP.__version__
        self.outString +=u"""<operator> %s </operator>\n"""%getpass.getuser()
        self.outString +=u"""<date> %s </date>\n"""%time.ctime()
        self.outString +=u"""<dataFile> %s </dataFile>\n"""%self.dbname
        self.outString +=u"""<lexicalFile> %s </lexicalFile>\n"""%self.lexical_kb
        self.outString +=u"""<tableName> %s </tableName>\n"""%self.table
        self.outString +=u"""<columnName> %s</columnName>\n"""%self.column
        self.outString +=u"""<domainFile> %s </domainFile>\n"""%self.domain_kb
        self.outString +=u"""</args"""
        self.run_time = time.asctime(time.localtime())

# create the tables for results and run arguments
        self.createTables()
        self.cursor.execute("""INSERT INTO run_args(run_date,label,args) VALUES (?,?,?)""",
                                    (self.run_time, self.result_label, self.outString,))

# get the run_args id for future REFERENCES
        self.cursor.execute("""SELECT rowid FROM run_args WHERE run_date = ?""",(self.run_time,))
        self.run_args_id = self.cursor.fetchone()[0]



# if the current schema is not in the table, then insert itemData
        # See if the current schema is already in the database
        try:
            self.cursor.execute("""SELECT rowid FROM class_schema WHERE schema = ?""",(self.classification_schema,))
            self.schema_id = self.cursor.fetchone()[0]
        except:
            self.cursor.execute("""INSERT INTO class_schema(schema) VALUES (?)""",(self.classification_schema,))
            self.schema_id = self._getLastRowID()
            #self.cursor.execute("""SELECT rowid FROM class_schema WHERE schema = ?""",(self.classification_schema,))
            #self.schema_id = self.cursor.fetchone()[0]


    def closeOutput(self):
        print "committing changes"
        self.conn.commit()
        print "closing connection"
        self.conn.close()
    def commitResults(self,rslts):#classification, positiveMarkup, documentMarkup):
        trslts = rslts[0]
	if( trslts ):
	    for key in trslts.keys():
                rslts = trslts[key]

		self.cursor.execute("""INSERT INTO pyConTextNLP_results(report_number,
                        run_args, schema, target_category, classification, most_positive_target) VALUES (?,?,?,?,?,?)""",
				(self.currentCase,self.run_args_id,self.schema_id, 
				 key, rslts[0], rslts[1],))
                if( rslts[2] ): # there are severity features
                    rslt_id = self._getLastRowID()
                    for r in rslts[2]:
                        self.cursor.execute("""INSERT INTO pyConTextNLP_severity(result,phrase,svalue,units) VALUES (?,?,?,?)""",
                                (rslt_id,r[0],r[1],r[2],))
        else:
            self.cursor.execute("""INSERT INTO pyConTextNLP_results(report_number,
                        run_args, schema, target_category, classification, most_positive_target) VALUES (?,?,?,?,?,?)""",
				(self.currentCase,self.run_args_id,self.schema_id,"NULL",0,"NULL",)) 
    def analyzeReport(self, report ):
        """
        given an individual radiology report, creates a pyConTextGraph
        object that contains the context markup
        report: a text string containing the radiology reports
        """
        context = self.document
        targets = self.targets
        modifiers = self.modifiers
        splitter = helpers.sentenceSplitter()
# alternatively you can skip the default exceptions and add your own
#       splitter = helpers.sentenceSpliter(useDefaults = False)
        #splitter.addExceptionTerms("Dr.","Mr.","Mrs.",M.D.","R.N.","L.P.N.",addCaseVariants=True)
        splitter.addExceptionTerms("Ms.","D.O.",addCaseVariants=True)
        splitter.deleteExceptionTerms("A.B.","B.S.",deleteCaseVariants=True)
        sentences = splitter.splitSentences(report)
        count = 0
        for s in sentences:
            #print s
            markup = pyConText.ConTextMarkup()
            markup.toggleVerbose()
            markup.setRawText(s)
            markup.cleanText()
            markup.markItems(modifiers, mode="modifier")
            markup.markItems(targets, mode="target")
            #raw_input('marked targets and modifiers')
            #print "markup before pruning"
            #print markup.getXML()
            markup.pruneMarks()
            markup.dropMarks('Exclusion')
            # apply modifiers to any targets within the modifiers scope
            markup.applyModifiers()

            markup.pruneSelfModifyingRelationships()
            #context.pruneModifierRelationships()
            #context.dropInactiveModifiers()
            # add markup to context document
            print markup
            context.addMarkup(markup)
            count += 1
        context.computeDocumentGraph()
        #print "*"*42
        #print context.getXML(currentGraph=False)
        #print "*"*42

    def processReports(self):
        """For the selected reports (training or testing) in the database,
        process each report 
        """
        for r in self.reports:
            #if r[0] in [77,2619,3030,3330]:
            self.document = pyConText.ConTextDocument()
            #try:
            if(True):
                self.currentCase = r[0]
                self.currentText = r[1].lower()
                print "CurrentCase:",self.currentCase
                print r[1].lower()
                self.analyzeReport(self.currentText)
                if( self.debug ):
                    self.writeDebugInfo()
                rslts = self.classifyDocumentTargets()
                self.commitResults(rslts)
                self.conn.commit()
            #except Exception, error:
                #print "error",error
                #print "failed to process report",r
                    
    def writeDebugInfo(self ):
        """write out an XML version of the current ConTextDocument markup for debugging purposes"""

        fout = open(os.path.join(self.debugDir,"%04d_debug.xml"%self.currentCase),"w")
        txt = self.document.getXML()
        try:
            xml = minidom.parseString(txt)
            fout.write(xml.toprettyxml(encoding=self.document.getUnicodeEncoding()))
        except Exception, error:
            print "could not prettify debug output", error
            fout.write(txt)
        fout.close()

    def classifyResult(self, docr):
        """given results in doc_rslts compare to classification_schema and return score.
        Takes a three-tuple of boolean values for Disease State Positive, Disease State Certain, Disease State Acute"""
        return assignSchema(docr,self.schema)
    def classifyDocumentTargets(self):
        """
        Look at the targets and their modifiers to get an overall classification for the document_markup
        """
        rslts = {} #[0,'']
        qualityInducedUncertainty = False
        document_markup = self.document.getXML()
        g = self.document.getDocumentGraph()
        targets = [n[0] for n in g.nodes(data = True) if n[1].get("category","") == 'target']

      
        if( targets ):
            neg_filters = ["definite_negated_existence","probable_negated_existence"]
            for t in targets:
                severityValues = []
                current_rslts = {}
                currentCategory = t.getCategory()
                if( not t.isA(["QUALITY_FEATURE","ARTIFACT"]) ):
                    for rk in self.class_rules:
                        current_rslts[rk] = genericClassifier(g,t,self.class_rules[rk])
                    for cr in self.category_rules:
                        anatomyRecategorize(g,t,cr)
                    for sv in self.severity_rules:
                        severity = getSeverity(g,t,sv)
                        severityValues.extend(severity)
                    currentCategory = t.categoryString()
                    print currentCategory
                    # now need to compare current_rslts to rslts to select most Positive
                    docr = self.classifyResult(current_rslts)
                    trslts = rslts.get(currentCategory,[-1,'',[]])
                    if( trslts[0] < docr ):
                        trslts = [docr,t.getXML(),severityValues]
                    rslts[currentCategory] = trslts 
                else:
                    if( t.isA('QUALITY_FEATURE')):
                        qualityInducedUncertainty = True
                    else:
                        if( not modifies(g,t,neg_filters) ):# non-negated artifacts
                            qualityInducedUncertainty = True
        # Need to fix this to reflect new representation
   #     if( qualityInducedUncertainty ): # if exam quality is described as limited, then always set certainty to be False
            #for key in rslts.keys():
                #rslts[key][1] = 0

        return rslts,document_markup


def getParser():
    """Generates command line parser for specifying database and other parameters"""

    parser = argparse.ArgumentParser(description="command line processer for processReports")
    parser.add_argument("-b","--db",dest='dbname',
                      help='name of Access database containing reports to parse.')
    parser.add_argument("-m","--mode",dest='mode',default='sqlite',
                      help="Database mode. Current supports 'sqlite' and 'access'")
    parser.add_argument("-l","--lexical_kb",dest='lexical_kb', nargs="*",
                      help='name of tab delimited file(s) containing lexical knowledge')
    parser.add_argument("-d","--domain_kb",dest='domain_kb', nargs="*",
                      help='name of tab delimited file(s) containing domain knowledge')
    parser.add_argument("-t","--table",dest='table',default='test_MyReports',
                      help='table in database to select data from')
    parser.add_argument("-i","--id",dest='id',default='reportid',
                      help='column in table to select identifier from')
    parser.add_argument("-c","--column",dest='report_text',default='report',
                      help='column in table to select report text from')
    parser.add_argument("-r","--result_label",dest="result_label",default="default",
                      help="result label for inserting into database")
    parser.add_argument("-g","--debug",dest="debug",action="store_true",default=False,
                      help="set debug to true for verbose output to text files")
    parser.add_argument("-s","--schema",dest="schema",default="",
                      help="file specifying schema")
    parser.add_argument("--rules",dest="rules",default="",
                      help="file specifying sentence level rules")
    return parser

def main():
    parser = getParser()
    options  = parser.parse_args()
    pec = criticalFinder(schema=options.schema,rules=options.rules,rid=options.id,column=options.report_text,table=options.table,result_label=options.result_label,
                         mode=options.mode,dbname=options.dbname,lexical_kb=options.lexical_kb,domain_kb=options.domain_kb,
                         debug=options.debug)
    pec.initializeOutput()
    pec.processReports()
    pec.closeOutput()


if __name__=='__main__':

    main()

