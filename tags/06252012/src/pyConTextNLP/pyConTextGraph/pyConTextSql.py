#Copyright 2010 Brian E. Chapman
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
"""
This module defines a class used for logical querying over a collection of sentences.
For the lack of knowing a better way of doing this, the sentences are dumped into a
sqlite database.
"""
import sqlite3 as sqlite
#import pyContext.pycontext as pycontext
import pyConTextGraph as pycontext
class pyConTextSql(object):
    def __init__(self, db = None ):
        """
        db is an optional filename for the database. If specified, a databse with the
        specfied filename is generated.
        
        Note: if an actual filename is specified, it is assumed that a corresponding
        databse does not exist. An exception will be thrown if the database exists
        and the object attempts to create tabels
        """
        if( db == None ):
            self.memory = True
            self.__conn = sqlite.connect(":memory:")
        else:
            self.memory = False
            self.__conn = sqlite.connect(db)
        self.__cursor = self.__conn.cursor()

        # create the table for sentences
        self.__cursor.execute("""CREATE TABLE sentences (
            id INT PRIMARY KEY,
            num INT NOT NULL,
            txt text)""")
        self.__cursor.execute("""CREATE TABLE foundTargets (
            id INTEGER PRIMARY KEY,
            sentence INTEGER NOT NULL REFERENCES "sentences" ("id"),
            term TEXT,
            unmodified VARCHAR(3) DEFAULT "NO")""")

    def populate(self,context,modifierFilters):
        """
        Given a context object, and columns to the foundTargets table corresponding to the
        modifiers listed in modiferFilters
        """
        for modfilter in modifierFilters:
                self.__cursor.execute("""ALTER TABLE foundTargets ADD COLUMN %s varchar(3) DEFAULT "NO" """%"'%s'"%modfilter)
                self.__cursor.execute("""ALTER TABLE foundTargets ADD COLUMN %s TEXT DEFAULT ''"""%"'%s TERM'"%modfilter)
                self.__cursor.execute("""ALTER TABLE foundTargets ADD COLUMN %s TEXT DEFAULT ''"""%"'%s PHRASE'"%modfilter)

        # insert sentences into sentence table
        for i in range(context.getNumberSentences()):
            context.setSentence(i)
            self.__cursor.execute("""INSERT INTO sentences (num,txt) VALUES (?,?)""",
                                    (i,context.getText(),))
            self.__cursor.execute("select last_insert_rowid() from sentences")
            sentid = i # self.__cursor.fetchone()[0]
            for tag in context.getConTextModeNodes("target"):    
                
                query = []
                values = []
                for modfilter in modifierFilters:
                    modifier = context.isModifiedBy(tag, modfilter)
                    if( modifier ):
                        query.extend(["'%s'"%modfilter,"'%s TERM'"%modfilter])
                        values.extend(['YES',modifier.__str__()]) 
                if( not query ):
                    self.__cursor.execute("""INSERT INTO foundTargets (sentence,term,unmodified) VALUES (?,?,?)""",
                                            (sentid,tag.getLiteral(),'YES',))
                else:
                    values.insert(0,sentid)
                    values.insert(1,tag.__str__())
                    v = ','.join(query)
                    p = ','.join(["?"]*len(query))
                    q = """INSERT INTO foundTargets (sentence,term,%s) VALUES (?,?,%s)"""%(v,p)
                    self.__cursor.execute(q,values)
        if( not self.memory ):
            self.__conn.commit()


    def query(self,query):
        """
        Submit query to the object to answer logical questions about the ConText markup.
        Currently the query is a SQL query fragment (the user should not provide the 'SELECT * from TABLENAME'
        to the foundTargets table database.
        s"""
        q = """SELECT * from foundTargets %s"""%query
        self.__cursor.execute(q)
        rslts = self.__cursor.fetchall()
        sentences = []
        data = []
        if( rslts ):
            for r in rslts:
                self.__cursor.execute("SELECT txt from sentences where num == %d"%r[1])
                data.append((r[1:],self.__cursor.fetchone()))
        return data
    
              
    def __str__(self):
        try:
            txt = ''

            self.__cursor.execute("select num,txt from sentences")
            sentences = self.__cursor.fetchall()
            for s in sentences:
                txt += "[%d]: %s\n"%(s[0],s[1])

            txt += "\n"
            self.__cursor.execute("PRAGMA table_info(foundTargets)")
            tInfo = self.__cursor.fetchall()

            self.__cursor.execute("""select * from foundTargets""")
            d = self.__cursor.fetchall()
            for dd in d:
                for i in range(len(tInfo)):
                    ddd = dd[i]
                    txt += "%s <<<%s>>> ||| "%(tInfo[i][1],ddd)
                txt += "\n"
            return txt
        except Exception, error:
            print "failed in __str__",error
            return txt
